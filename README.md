pyinstaller --noconsole --onefile `
  --add-data "src;src" `
  --collect-all streamlit `
  run.py