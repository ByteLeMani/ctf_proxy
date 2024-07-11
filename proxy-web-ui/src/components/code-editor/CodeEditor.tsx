

import { Editor, useMonaco } from "@monaco-editor/react";
import { useEffect } from "react";
import * as Monaco from 'monaco-editor';

export default function CodeEditor() {

  const monaco = useMonaco();

  useEffect(() => {
    // do conditional chaining
    monaco?.languages.typescript.javascriptDefaults.setEagerModelSync(true);
    // or make sure that it exists by other ways
    if (monaco) {
      console.log('here is the monaco instance:', monaco);
      
    }
  }, [monaco]);

  // https://microsoft.github.io/monaco-editor/typedoc/interfaces/editor.IStandaloneEditorConstructionOptions.html
  const editorOptions = Monaco.editor.IStandaloneEditorConstructionOptions = {
    // Configuration options go here
    language: 'python', // Example: Set the language mode to JavaScript
    automaticLayout: true, // Example: Enable automatic layout
    fontSize: 16, // Example: Set font size to 16px
    readOnly: false,
    minimap: { enabled: false }
};



  return (
    <Editor
    options={editorOptions}
      width="100vh"
      height="30vh"
      defaultLanguage="python"
      defaultValue="def username(self, stream: HTTPStream):
    message = stream.current_http_message
    if 'register' in message.url and 'POST' in message.method:
        username = message.parameters.get('username')
        if len(username) > 10:
            return True
    else:
        return False"
    />
  );
}