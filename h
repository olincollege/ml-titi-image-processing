<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="https://pyscript.net/latest/pyscript.css" />
  <script defer src="https://pyscript.net/latest/pyscript.js"></script>
</head>

<body>
  <h1>Browser Python Notebook</h1>

  <textarea id="code" style="width:100%; height:150px;">
print("hello from browser python")
  </textarea>

  <button py-click="run_code()">Run</button>

  <div id="output"></div>

  <py-script>
from pyscript import Element

def run_code():
    code = Element("code").element.value
    output = Element("output")

    try:
        exec(code)
    except Exception as e:
        output.write(str(e))
  </py-script>
</body>
</html>
