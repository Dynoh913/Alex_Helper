Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\ADMIN\voice-assistant"
WshShell.Run """C:\Users\ADMIN\voice-assistant\.venv\Scripts\pythonw.exe"" ""C:\Users\ADMIN\voice-assistant\voice_assistant.py""", 0, False
