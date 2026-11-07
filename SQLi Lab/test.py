import re

txt = "User Exist.jdısajdsaıodjnsaolıkdjsaışoldjasoıdasjod"

if re.search("^User Exist$.", txt):
    print("Match Found")