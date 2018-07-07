from django.test import TestCase

# Create your tests here.
import diff_match_patch as dmp_module

dmp = dmp_module.diff_match_patch()
diff = dmp.diff_main("Hello World.", "Goodbye World.")
# Result: [(-1, "Hell"), (1, "G"), (0, "o"), (1, "odbye"), (0, " World.")]
dmp.diff_cleanupSemantic(diff)
# Result: [(-1, "Hello"), (1, "Goodbye"), (0, " World.")]
print(diff)
print(dmp.diff_prettyHtml(diff))
# -1 表示删除， 1 表示插入, 0表示相等
# 从 Hello World 变成Goodbye World需要删除 Hello 插入Goodbye
#