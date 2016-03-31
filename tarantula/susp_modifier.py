filename = "programs/totinfo/source.alt/source.orig/tot_info.c"


class SuspModifier(object):
    def __init__(self, filename):
        self._filename = filename

    def get_if_lines(self):
        # 0th line empty so we can index by 1
        lines = [""]
        with open(self._filename, 'r') as fd:
            lines += fd.readlines()

        lines = [l.strip() for l in lines]

        if_lines = []
        for i, l in enumerate(lines):
            if l.strip().startswith("if"):
                if_lines.append(i)
                
        return if_lines

    def modify_susp(self, suspiciousness):
        ordered_lines = sorted(suspiciousness.keys())
        if_lines = set(self.get_if_lines())

        for i, line in enumerate(ordered_lines):
            if line in if_lines and i + 1 < len(ordered_lines):
                nextline = ordered_lines[i + 1]
                print("Changing line {0} susp to {1}".format(line, nextline))

                newsusp = max(suspiciousness[line], suspiciousness[nextline])
                suspiciousness[line] = newsusp
        return suspiciousness
