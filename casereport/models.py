from collections import namedtuple
from datetime import datetime

from access_tokens import tokens
from actstream import action as actstream_action
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.db import models
from django.template.loader import render_to_string
from django.utils.encoding import python_2_unicode_compatible
from django_countries.fields import CountryField
from django_fsm import signals as fsm_signals
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by
from django_fsm_log.models import StateLog
from djangocms_text_ckeditor.fields import HTMLField

from casereport import emails
from casereport.constants import (GENDER, OBJECTIVE_RESPONSES,
                                  PERFORMANCE_STATUS, TREATMENT_INTENT, TYPE,
                                  WorkflowState)
from casereport.middleware import CurrentUserMiddleware
from rlp.accounts.models import User
from rlp.core.models import SharedObjectMixin
from rlp.discussions.models import ThreadedComment

from .utils import past_tense_verb

__author__ = 'yaseen'

ACTION_QUEUE = []
QueuedAction = namedtuple('QueuedAction', 'sender kwargs')


class ActionWrapper(object):
    """ stand-in for actstream.action which queues the actions
        and records the object's state if it has a to_dict member.

        Remember to call action.really_send to record these actions.
    """
    @staticmethod
    def send(sender, **kwargs):
        global ACTION_QUEUE
        ACTION_QUEUE.append(QueuedAction(sender=sender, kwargs=kwargs))

    @staticmethod
    def really_send():
        global ACTION_QUEUE
        while ACTION_QUEUE:
            qa = ACTION_QUEUE.pop(0)

            obj = qa.kwargs.get('action_object', None)
            data = False
            if obj:
                if hasattr(obj, 'to_dict'):
                    data = obj.to_dict()
            qa.kwargs['frozen'] = data
            actstream_action.send(qa.sender, **qa.kwargs)


action = ActionWrapper()


@python_2_unicode_compatible
class CRDBBase(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)


@python_2_unicode_compatible
class Institution(CRDBBase):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    country = CountryField()
    address = models.TextField()

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Physician(CRDBBase):
    affiliation = models.ForeignKey(Institution, null=True, blank=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()

    def __str__(self):
        return str(self.name) or ''

    def get_name(self):
        return self.name

    def get_country(self):
        if self.affiliation:
            return self.affiliation.country.name.capitalize()
        return None

    def get_country_code(self):
        if self.affiliation:
            return self.affiliation.country.code
        return None

    def get_rlpuser(self):
        try:
            user = User.objects.get(email=self.email)
            return user.pk
        except User.DoesNotExist:
            return None


@python_2_unicode_compatible
class CaseFile(CRDBBase):
    name = models.CharField(max_length=200)
    document = models.FileField()

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class MolecularAbberation(CRDBBase):
    name = models.CharField(max_length=255)
    # molecule field no longer used but needs to be kept for migrations
    molecule = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Genetic Aberration'
        verbose_name_plural = 'Genetic Aberrations'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class SubtypeOption(CRDBBase):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class AuthorizedRep(CRDBBase):
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField()

    def __str__(self):
        return self.email

    def get_name(self):
        return self.email


class CaseReportReview(models.Model):
    discussions = GenericRelation(
        ThreadedComment,
        object_id_field='object_pk',
    )

    def __str__(self):
        return 'Editorial Note: {}'.format(self.casereport)

    def get_absolute_url(self):
        return reverse('review', args=(self.casereport.id,))


@python_2_unicode_compatible
class CaseReport(CRDBBase, SharedObjectMixin):
    title = models.CharField(max_length=500,
                             null=True,
                             blank=True,
                             verbose_name='Case Title')
    gender = models.CharField(max_length=20,
                              choices=GENDER,
                              null=True,
                              blank=True)
    age = models.IntegerField(null=True, blank=True)
    primary_author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='primary_case',
        verbose_name='Case Report Author')
    co_author = models.ManyToManyField(
        User,
        blank=True,
        verbose_name='Case Report Co-Authors')
    authorized_reps = \
        models.ManyToManyField(AuthorizedRep,
                               blank=True,
                               verbose_name='Alternative Correspondence ' +
                                            'Email Address')
    subtype = models.ForeignKey(SubtypeOption, models.SET_NULL,
                                null=True, blank=True)
    subtype_other = models.CharField(max_length=500, null=True, blank=True)
    presentation = models.TextField(null=True, blank=True)
    aberrations = models.ManyToManyField(MolecularAbberation, blank=True)
    aberrations_other = models.CharField(max_length=500, null=True, blank=True)
    biomarkers = models.TextField(null=True, blank=True)
    pathology = HTMLField(null=True, blank=True)
    additional_comment = models.TextField(null=True, blank=True)

    # Workflow control fields
    author_approved = models.BooleanField(default=False, blank=True)
    admin_approved = models.BooleanField(default=False, blank=True)
    workflow_state = FSMField(max_length=50,
                              choices=WorkflowState.CHOICES,
                              default=WorkflowState.INITIAL_STATE,
                              help_text="Workflow state")

    casefile_f = models.FileField(null=True, blank=True)
    free_text = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True, db_index=True)
    date_updated = models.DateTimeField(auto_now=True, db_index=True)
    date_published = models.DateTimeField(db_index=True, null=True, blank=True)
    attachment1 = models.FileField(null=True, blank=True)
    attachment1_title = models.CharField(max_length=500, null=True, blank=True)
    attachment1_description = models.TextField(null=True, blank=True)
    attachment2 = models.FileField(null=True, blank=True)
    attachment2_title = models.CharField(max_length=500, null=True, blank=True)
    attachment2_description = models.TextField(null=True, blank=True)
    attachment3 = models.FileField(null=True, blank=True)
    attachment3_title = models.CharField(max_length=500, null=True, blank=True)
    attachment3_description = models.TextField(null=True, blank=True)
    consent = models.BooleanField(default=False, blank=True)
    discussions = GenericRelation(
        ThreadedComment,
        object_id_field='object_pk',
    )
    review = models.OneToOneField(
        CaseReportReview,
        related_name='casereport',
        null=True,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.title if self.title else '---'

    def to_dict(self):
        # this gets us the latest state change, but it doesn't yet
        # have the state change we are undergoing
        # so we have to save the "previous_statelog_id"
        try:
            sl = StateLog.objects.for_(self).order_by('-timestamp')[0]
        except IndexError as too_new:
            sl = None
        return {
            'model': 'CaseReport',
            'id': self.id,
            'title': self.title,
            'author_approved': self.author_approved,
            'admin_approved': self.admin_approved,
            'date_published': self.date_published.strftime("%m/%d/%Y")
            if self.date_published else None,
            'workflow_state': self.workflow_state,
            # these are slightly redundant but included for debugging
            'statelog_transition': sl.transition if sl else None,
            'statelog_state': sl.state if sl else None,
            'statelog_id': sl.id if sl else None,
        }

    def share_with(self, viewers, shared_by,
                   exclude=[],
                   comment=None,
                   publicly=True,
                   force_public=False):
        """ share with viewers by shared_by
            This accepts publicly only for the interface.
            Instead, this marks the shares as Private if the CR is not LIVE
        """
        public_sharing = force_public or self.workflow_state == WorkflowState.LIVE
        return super(CaseReport, self).share_with(viewers,
                                                  shared_by,
                                                  exclude=exclude,
                                                  comment=comment,
                                                  publicly=public_sharing)

    def sort_date(self):
        if self.date_published:
            return self.date_published
        else:
            return self.date_updated

    # Workflow related methods
    def get_workflow_icon(self):
        return WorkflowState.ICONS.get(self.workflow_state, "")

    def can_view(self, user=None):
        if not user:
            user = CurrentUserMiddleware.get_user()
        return (user.email == self.primary_author.email) or user.is_staff

    def can_edit(self, user=None):
        if not user:
            user = CurrentUserMiddleware.get_user()
        if self.workflow_state in (WorkflowState.DRAFT,
                                   WorkflowState.RETRACTED,
                                   WorkflowState.AUTHOR_REVIEW) and \
           user.email == self.primary_author.email:
            return True
        if self.workflow_state in (WorkflowState.ADMIN_REVIEW,) and \
           user.is_staff:
            return True
        return False

    @fsm_log_by
    @transition(field=workflow_state,
                source=[WorkflowState.DRAFT],
                permission=can_edit,
                target=WorkflowState.DRAFT
                )
    def edit(self, by=None):
        pass

    @fsm_log_by
    @transition(field=workflow_state,
                source=[WorkflowState.AUTHOR_REVIEW, WorkflowState.RETRACTED],
                permission=can_edit,
                target=WorkflowState.AUTHOR_REVIEW
                )
    def author_review_edit(self, by=None):
        pass

    @fsm_log_by
    @transition(field=workflow_state,
                source=[WorkflowState.ADMIN_REVIEW],
                permission=can_edit,
                target=WorkflowState.ADMIN_REVIEW
                )
    def admin_edit(self, by=None):
        pass

    def can_submit(self, user=None):
        # ensure author
        if not user:
            user = CurrentUserMiddleware.get_user()
        return user.email == self.primary_author.email

    @fsm_log_by
    @transition(field=workflow_state,
                source=[WorkflowState.AUTHOR_REVIEW, ],
                permission=can_submit,
                target=WorkflowState.ADMIN_REVIEW)
    def approve(self, by=None):
        """ send to admins with approval """
        self.author_approved = True
        self.admin_approved = False
        try:
            emails.approved(self)
        except Exception as mail_err:
            print(mail_err)

        return "Thank you for approving your Case Report. We will contact you" \
               " when it goes live."

    @fsm_log_by
    @transition(field=workflow_state,
                source=[WorkflowState.DRAFT, ],
                permission=can_submit,
                target=WorkflowState.ADMIN_REVIEW)
    def submit(self, by=None):
        """ send to admin without approval """
        self.author_approved = True
        self.admin_approved = False
        try:
            emails.submitted(self)

            # notify co-authors
            for coauthor in self.co_author.all():
                if coauthor.is_active:
                    emails.notify_coauthor(self, coauthor)
                else:
                    emails.invite_coauthor(self, coauthor)
        except ConnectionRefusedError:
            print("cannot connect to email")
        return "Your Case Report has been submitted and will be reviewed by \
            our admin staff. \
            Please note case no. #%s for future reference." % self.id

    def can_reject(self, user=None):
        if not user:
            user = CurrentUserMiddleware.get_user()
        if user.is_staff \
           and self.workflow_state in (WorkflowState.ADMIN_REVIEW,):
            return True
        return False

    @fsm_log_by
    @transition(field=workflow_state,
                source=[WorkflowState.ADMIN_REVIEW, ],
                permission=can_reject,
                target=WorkflowState.AUTHOR_REVIEW,
                )
    def send_back(self, by=None):
        """ send the CR back to the author
        """
        self.admin_approved = False
        try:
            emails.send_back(self)
        except ConnectionRefusedError:
            pass
        user = CurrentUserMiddleware.get_user()
        author = User.objects.get(email__exact=self.primary_author.email)
        action.send(user, verb='sent back', action_object=self, target=author)
        return "The case report has been sent back to its author."

    def can_publish(self, user=None):
        # ensure admin
        if not user:
            user = CurrentUserMiddleware.get_user()
        return user.is_staff

    @fsm_log_by
    @transition(field=workflow_state,
                source=[WorkflowState.ADMIN_REVIEW, ],
                permission=can_publish,
                target=WorkflowState.LIVE)
    def publish(self, by=None):
        self.admin_approved = True
        author = User.objects.get(email__exact=self.primary_author.email)
        self.share_with(self.co_author.all(), shared_by=author)

        # re-share publicly with the author's private shares
        # remember, we're still in the source state so our state is not yet LIVE
        those_notified = []
        for npshare in self.get_nonpublished_shares():
            target = npshare.target
            invite_msg = npshare.description
            notified = self.share_with([target],
                                       shared_by=self.primary_author,
                                       exclude=those_notified,
                                       comment=invite_msg,
                                       force_public=True)
            those_notified.extend(notified)

        if not self.date_published:
            # only send these emails on first publish
            try:
                emails.cr_published_notifications(self)
            except ConnectionRefusedError:
                pass
        self.date_published = datetime.now()
        try:
            emails.publish_to_author(self)
        except ConnectionRefusedError:
            pass

        user = CurrentUserMiddleware.get_user()
        action.send(user, verb='published', action_object=self, target=author)
        return "This case report has been published!"

    def can_retract_as_author(self, user=None):
        # ensure author or admin
        if not user:
            user = CurrentUserMiddleware.get_user()
        return user.email == self.primary_author.email

    def can_retract_as_admin(self, user=None):
        # ensure author or admin
        if not user:
            user = CurrentUserMiddleware.get_user()
        return user.is_staff

    @fsm_log_by
    @transition(field=workflow_state,
                source=[WorkflowState.RETRACTED],
                permission=can_retract_as_author,
                target=WorkflowState.AUTHOR_REVIEW)
    def _retract_by_author(self, by=None):  # starts with _ to hide from users
        self.author_approved = False
        # self.notify_datascience_team()
        return '''pulled back'''

    @fsm_log_by
    @transition(field=workflow_state,
                source=[WorkflowState.RETRACTED],
                permission=can_retract_as_admin,
                target=WorkflowState.ADMIN_REVIEW)
    def _retract_by_admin(self, by=None):  # starts with _ to hide from users
        """ unpublish """
        self.admin_approved = False
        user = CurrentUserMiddleware.get_user()
        author = User.objects.get(email__exact=self.primary_author.email)
        action.send(user, verb='unpublished', action_object=self, target=author)
        return '''pulled back'''

    def can_retract(self, user=None):
        if not user:
            user = CurrentUserMiddleware.get_user()
        return self.can_retract_as_author(user) or self.can_retract_as_admin(user)

    @fsm_log_by
    @transition(field=workflow_state,
                source=[WorkflowState.LIVE],
                permission=can_retract,
                target=WorkflowState.RETRACTED)
    def revise(self, by=None):
        """ uses the current user to choose between retract_by_author and
            retract_by_admin
        """
        user = CurrentUserMiddleware.get_user()
        self.author_approved = True
        self.admin_approved = False
        try:
            emails.revise(self, user)
        except Exception as mail_err:
            print(mail_err)
        return "Retracted"

    #  TODO:think hard about moving these out of the model and into WorkflowState
    def _get_displayname_for_fname(self, fname):
        """ turn a Transition name into its associated method name.
        """
        return fname.title().replace('_', ' ')

    def _get_fname_for_displayname(self, displayname):
        """ turn a transition method name into its assocated Display Name.
        """
        return displayname.lower().replace(' ', '_')

    def get_next_actions_for_user(self, user=None):
        if not user:
            user = CurrentUserMiddleware.get_user()
        workflow_transitions = \
            self.get_available_user_workflow_state_transitions(user)
        # suppress private transitions and make then displayable
        return [self._get_displayname_for_fname(fsmo.name) for fsmo in
                workflow_transitions if not fsmo.name[0] == '_']

    def take_action_for_user(self, action_name, user=None, group=None):
        if not user:
            user = CurrentUserMiddleware.get_user()

        if action_name not in self.get_next_actions_for_user(user=user):
            raise KeyError(action_name)

        verb = past_tense_verb(action_name)

        transition_function = getattr(self, self._get_fname_for_displayname(action_name))
        res = transition_function(by=user)

        # RETRACTED is a transitory state. If we have landed in that state,
        # then we must determine which fork in the workflow to take.
        # We dont just get the next and recurse on it to avoid multiple
        # messages and actions getting recorded.
        if self.workflow_state == WorkflowState.RETRACTED:
            if self.can_retract_as_author():
                verb = self._retract_by_author(by=user)
                res = "Case report has been pulled back"
            elif self.can_retract_as_admin():
                verb = self._retract_by_admin(by=user)
                res = "Case report has been pulled back"
            else:
                raise PermissionError("permission denied")

        if group:
            action.send(user, verb=verb, action_object=self, target=group)
        else:
            action.send(user, verb=verb, action_object=self)

        return res

    @property
    def display_type(self):
        return "Case Report"

    def save(self, *args, **kwargs):
        if not self.review:
            self.review = CaseReportReview.objects.create()
        super(CaseReport, self).save(*args, **kwargs)

    def notify_datascience_team(self):
        subject = settings.NEW_CASE
        if self.workflow_state != WorkflowState.DRAFT:
            subject = settings.EDITED
        message_body = render_to_string('casereport/admin_notify.html',
                                        {'title': self.title,
                                         'status': self.workflow_state,
                                         'name': self.primary_author.get_full_name()})
        recipient_members = settings.DATA_SCIENCE_TEAM
        for member in recipient_members:
            message = EmailMessage(subject,
                                   message_body,
                                   settings.DEFAULT_FROM_EMAIL,
                                   [member])
            message.content_subtype = 'html'
            message.send()

    def send_review_mail(self):
        history_obj = CaseReportHistory.objects.filter(case=self.id).last()
        token = tokens.generate(scope=(), key=self.id,
                                salt=settings.TOKEN_SALT)
        Headers = {'Reply-To': settings.SERVER_EMAIL}
        recipients = list(self.authorized_reps.all())
        primary_recipient = self.primary_author
        subject = settings.CASE_READY_SUBJECT
        if self.workflow_state == WorkflowState.ADMIN_REVIEW and not history_obj:
            for recipient in recipients:
                if recipient.email:
                    message = render_to_string(
                        'casereport/email_to_authorized.html',
                       {'id': self.id,
                        'title': self.title,
                        'name': recipient.get_name(),
                        'token': token,
                        'DOMAIN': getattr(settings, 'DOMAIN', ''),
                        'Date': self.created_on,
                        'primary_author': self.primary_author.get_name()
                                                })
                    msg = EmailMessage(subject,
                                       message,
                                       settings.SERVER_EMAIL,
                                       [recipient.email],
                                       headers=Headers,
                                       cc=[primary_recipient.email]
                                       )
                    msg.content_subtype = "html"
                    msg.send()
        if self.workflow_state == WorkflowState.LIVE:
            subject = settings.CASE_APPROVED_SUBJECT
        authorized_emails = []
        for entry in recipients:
            authorized_emails.append(str(entry))
        message = render_to_string('casereport/email_to_author.html',
                                   {'id': self.id,
                                    'title': self.title,
                                    'name': primary_recipient.get_name(),
                                    # 'token': token,
                                    'DOMAIN': getattr(settings,'DOMAIN',''),
                                    'Date': self. created_on,
                                    'status': self.status,
                                    'history_object': history_obj,
                                    })
        msg = EmailMessage(subject,
                           message,
                           settings.SERVER_EMAIL,
                           [primary_recipient.email],
                           headers=Headers, cc=authorized_emails,
                           bcc=settings.BCC_LIST
                           )
        msg.content_subtype = "html"
        msg.send()

    def ordered_event(self, event_type):
        events = []
        try:
            event = Event.objects.get(casereport_f=self, previous_event=None,
                                      parent_event=None)
        except:
            return events
        while(event.next_event):
            if event.event_type == event_type and event.is_negation == False:
                events.append(event)
            event = event.next_event
        if event.event_type == event_type and event.is_negation == False:
            events.append(event)
        return events

    def get_treatments(self):
        return Treatment.objects.filter(casereport_f=self)

    def attch_is_image(self, filename):
        ext = filename.split('.')[-1:]
        return ext[0].lower() in ['jpg', 'gif', 'png', 'jpeg']

    def get_attachments(self):
        if not (self.attachment1 or self.attachment2 or self.attachment3):
            return []
        attachments = []
        if self.attachment1:
            attachments.append({
                'id': 'attachment1',
                'file': self.attachment1,
                'title': self.attachment1_title,
                'description': self.attachment1_description,
                'is_image': self.attch_is_image(self.attachment1.url)})
        if self.attachment2:
            attachments.append({
                'id': 'attachment2',
                'file': self.attachment2,
                'title': self.attachment2_title,
                'description': self.attachment2_description,
                'is_image': self.attch_is_image(self.attachment2.url)})
        if self.attachment3:
            attachments.append({
                'id': 'attachment3',
                'file': self.attachment3,
                'title': self.attachment3_title,
                'description': self.attachment3_description,
                'is_image': self.attch_is_image(self.attachment3.url)},)
        return attachments

    def get_treatment_events_in_order(self):
        return self.ordered_event('treatment')

    def get_test_events_in_order(self):
        return self.ordered_event('test')

    def get_diagnosis_events_in_order(self):
        return self.ordered_event('diagnosis')

    def get_author(self):
        return self.primary_author.get_full_name()

    def get_coauthors(self):
        coauthors = []
        for ref in self.co_author.all():
            if ref.pk != self.primary_author.pk:
                coauthors.append(ref)
        return coauthors

    def get_presented(self):
        event = Event.objects.filter(casereport_f=self,
                                     parent_event__isnull=True)
        return event[0].get_info()

    def get_reported_date(self):
        try:
            event = Event.objects.get(casereport_f=self, parent_event=None)
        except:
            event = None
        return event.date_point if event else event

    def get_absolute_url(self):
        from django.utils.text import slugify
        slug = slugify(self.title)
        return reverse(
            'casereport_detail',
            kwargs={'case_id': self.pk, 'title_slug': slug},
        )


## TODO: can we move this someplace more obvious?
def casereport_workflow_transitions(sender, **kwargs):
    # this is the hook that should handle all side effects of state change
    # transitions like sending emails, clearing queues, etc.
    cr = kwargs['instance']
    transition_name = kwargs['name']
    source_state = kwargs['source']
    end_state = kwargs['target']
    if end_state != source_state:
        print("handling %s transition for %s" % (transition_name, cr))
        print("...TODO...\n\n")


fsm_signals.post_transition.connect(casereport_workflow_transitions,
                                    sender=CaseReport)



@python_2_unicode_compatible
class Treatment(CRDBBase):
    casereport_f = models.ForeignKey(
        CaseReport, verbose_name='Case Report', default=1
    )
    name = models.CharField(max_length=250)
    treatment_type = models.CharField(max_length=250)
    duration = models.CharField(max_length=250, null=True, blank=True)
    treatment_intent = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=TREATMENT_INTENT)
    objective_response = models.CharField(
        max_length=50,
        choices=OBJECTIVE_RESPONSES,
        null=True,
        blank=True)
    status = models.IntegerField(
        choices=PERFORMANCE_STATUS,
        null=True,
        blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Event(CRDBBase):
    casereport_f = models.ForeignKey(
        CaseReport, verbose_name='Case Report', default=1
    )
    parent_event = models.ForeignKey('self', null=True, blank=True, related_name="parentevent")
    name =  models.CharField(max_length=255)
    frequency = models.IntegerField(null=True, blank=True)
    date_point = models.CharField(max_length=200, null=True, blank=True)  # (year, or actual date)
    end_date_point = models.CharField(max_length=200, null=True, blank=True)  # (year, or actual date)
    interval = models.CharField(max_length=200, null=True, blank=True)  # (e.g. 6 months of therapy)
    previous_event = models.ForeignKey('self', null=True, blank=True, related_name="previousevent")  # use this instead of order
    next_event = models.ForeignKey('self', null=True, blank=True, related_name="nextevent")
    is_negation = models.BooleanField(default=False)
    event_type = models.CharField(max_length=15, choices=TYPE, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_treatment_type(self):
        return self.treatmentevent.treatment_type

    def get_side_effects(self):
        side_effects = self.treatmentevent.side_effects
        return side_effects if side_effects else None

    def get_outcome(self):
        event = self.treatmentevent
        outcome = event.outcome
        while(event.combined_with):
            event = event.combined_with
            outcome = '%s, %s' %(outcome, event.outcome)
        if outcome.strip(', ') == '':
            outcome = ''
        else:
            outcome = outcome.strip(', ')
        return outcome


    def get_name(self):
        event = self.treatmentevent
        name = event.name
        while(event.combined_with):
            name = '%s / %s' %(name, event.combined_with)
            event = event.combined_with
        return name

    def get_combined_with(self):
        return self.treatmentevent.combined_with

    def get_dates(self):
        dates = ''
        if self.date_point:
            dates =  '%s' %self.date_point
        if self.end_date_point:
            dates = '%s' % self.end_date_point
        if (self.date_point and self.end_date_point):
            dates = '%s - %s' %(self.date_point, self.end_date_point)
        return '%s:' %dates if dates else ''

    def get_test_specimen(self):
        specimen = self.testevent.specimen
        return specimen if specimen else 'specimen (Not Specified)'

    def get_body_part(self):
        body_part = self.testevent.body_part
        return body_part if body_part else 'body part (Not Specified)'

    def get_diagnosis_specimen(self):
        specimen = self.diagnosisevent.specimen
        return specimen if specimen else 'specimen (Not Specified)'

    def get_symptoms(self):
        diagnosis = self.diagnosisevent
        symptoms = diagnosis.symptoms
        if diagnosis.body_part:
            symptoms += ' (%s)' %diagnosis.body_part
        return symptoms if symptoms else 'symptoms (Not Specified)'

    def get_test_results(self):
        results = ''
        for result in ResultValueEvent.objects.filter(test=self.testevent):
            value = result.value
            if result.result_indicator:
                value += ' (%s)' %result.result_indicator
            results =  '%s, %s' %(results, value) if results else value
        if not results:
            results = 'results (Not Specified)'
        return results

    def get_info(self):
        if self.date_point:
            return '%s on %s' %(self.name, self.date_point)
        return ''



@python_2_unicode_compatible
class TestEvent(Event):
    specimen = models.CharField(max_length=255)
    body_part = models.CharField(max_length=255, null=True, blank=True)

    def save(self):
        self.event_type = 'test'
        super(TestEvent, self).save()


@python_2_unicode_compatible
class TreatmentEvent(Event):
    treatment_type = models.CharField(max_length=255)
    followed_by = models.ForeignKey('self', null=True, blank=True)  # - Treatment Event
    followed_by_interval = models.CharField(max_length=50, null=True, blank=True)
    followed_by_interval_unit = models.CharField(max_length=100, null=True, blank=True)
    combined_with = models.ForeignKey('self', null=True, blank=True, related_name="combinedwith")
    side_effects = models.TextField(null=True, blank=True)
    outcome = models.TextField(null=True, blank=True)

    def save(self):
        self.event_type = 'treatment'
        super(TreatmentEvent, self).save()


@python_2_unicode_compatible
class ResultValueEvent(CRDBBase):
    test = models.ForeignKey(TestEvent)  # FK (Test Event)
    value = models.CharField(max_length=200)  # 15.6
    result_indicator = models.CharField(max_length=200, null=True,
                                        blank=True)  # high, low, normal (if available or will be null)

    def __str__(self):
        return self.value


@python_2_unicode_compatible
class DiagnosisEvent(Event):
    test = models.ForeignKey(TestEvent, null=True, blank=True)
    specimen = models.CharField(max_length=255, null=True, blank=True)
    symptoms = models.TextField(null=True, blank=True)
    body_part = models.CharField(max_length=255, null=True, blank=True)

    def save(self):
        self.event_type = 'diagnosis'
        super(DiagnosisEvent, self).save()


@python_2_unicode_compatible
class CaseReportHistory(models.Model):
    case = models.ForeignKey(CaseReport)
    physician = models.TextField(null=True, blank=True)
    molecular_abberations = models.TextField(null=True, blank=True)
    tests = models.TextField(null=True, blank=True)
    treatments = models.TextField(null=True, blank=True)
    diagnosis = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.case) or ''
