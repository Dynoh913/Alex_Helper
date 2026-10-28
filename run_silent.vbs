Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\ADMIN\voice-assistant"
WshShell.Run """.venv\Scripts\pythonw.exe"" voice_assistant.py", 0, False
