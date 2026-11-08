from prompt import build_prompt

context = """
Weed control methods include
1. Cultural
2. Mechanical
3. Chemical
4. Biological
"""

question = "How to control weeds?"

prompt = build_prompt(context, question)

print(prompt)