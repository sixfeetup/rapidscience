import sys
import re
from django.template.loader import  get_template
# from django.core.management import execute_from_command_line
import django

INCLUDE_PATTERN = re.compile(r'''({% include ["']([^"]+)["'] %})''',)
VAR_PATTERN = re.compile(r'''({{ (.*?) }})''')

def includerize(src):
    body = src.split("\n")
    new_body = []
    for line in body:
        m = INCLUDE_PATTERN.search(line)
        if m:
            # import pdb; pdb.set_trace()
            filename = m.groups()[1]
            print("including " + filename )
            include_template = get_template(filename)

            # import pdb; pdb.set_trace()
            include_txt = includerize(include_template.template.source)
            line = line.replace(m.groups()[0], include_txt)
        # print(line)
        new_body.append(line)
    return "\n".join(new_body)



def optimize(src):
    """ find overuses of dots """
    exprs = VAR_PATTERN.findall(src)
    counts = {}
    for e in exprs:
        counts[e[1]] = counts.setdefault(e[1], 0) + 1
    # import pdb; pdb.set_trace()
    from pprint import pprint as pp
    # pp(sorted(counts))

    for key, value in sorted(counts.items(), key=lambda kv: kv[0]):
        print( "%s: %s" % (key, value) )

    print("\n\nby val")
    for key, value in sorted(counts.items(), key=lambda kv: kv[1]):
        print( "%s: %s" % (key, value) )



if __name__ == '__main__':
    django.setup()
    t = get_template(sys.argv[1])
    tnew = includerize(t.template.source)
    optimize(tnew)

