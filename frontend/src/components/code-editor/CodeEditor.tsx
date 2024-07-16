/* --------------------------------------------------------------------------------------------
 * Copyright (c) 2024 TypeFox and others.
 * Licensed under the MIT License. See LICENSE in the package root for license information.
 * ------------------------------------------------------------------------------------------ */

import * as vscode from 'vscode';
import { RegisteredFileSystemProvider, registerFileSystemOverlay, RegisteredMemoryFile } from '@codingame/monaco-vscode-files-service-override';
import React, { StrictMode, useCallback, useState } from 'react';
import ReactDOM from 'react-dom/client';
import type { TextChanges } from '@typefox/monaco-editor-react';
import { MonacoEditorReactComp } from '@typefox/monaco-editor-react';
import { useWorkerFactory } from 'monaco-editor-wrapper/workerFactory';
import { MonacoEditorLanguageClientWrapper } from 'monaco-editor-wrapper';
import { createUserConfig } from './config.js';
import codePyCode from './code.py?raw';
import { Filter } from '../../models/Filter.js';
import { UserConfig } from 'monaco-editor-wrapper';
import {editor} from 'monaco-editor'

export const configureMonacoWorkers = () => {
    useWorkerFactory({
        ignoreMapping: true,
        workerLoaders: {
            editorWorkerService: () => new Worker(new URL('monaco-editor/esm/vs/editor/editor.worker.js', import.meta.url), { type: 'module' }),
        }
    });
};

interface EditorProps {
    pattern: string;
    setEditor: React.Dispatch<React.SetStateAction<editor.IStandaloneCodeEditor | undefined>>;
}

export default function CodeEditor({pattern, setEditor}:EditorProps){
    const codePyUri = vscode.Uri.file('/workspace/code.py');
    const fileSystemProvider = new RegisteredFileSystemProvider(false);
    fileSystemProvider.registerFile(new RegisteredMemoryFile(codePyUri, codePyCode));
    registerFileSystemOverlay(1, fileSystemProvider);
    
    const codePy = {
        code: pattern, // `def test():            pass`,
        uri: vscode.Uri.file("/workspace/code.py"),
      };

    const onTextChanged = (textChanges: TextChanges) => {
        // setNewFilter({...filter, pattern: textChanges.main});
        console.log(`Dirty? ${textChanges.isDirty}\ntext: ${textChanges.main}\ntextOriginal: ${textChanges.original}`);
    };


    return <MonacoEditorReactComp
        userConfig={createUserConfig('/workspace', codePy.code, codePy.uri.toString())}
        style={{
            'paddingTop': '5px',
            'height': '80vh',
            'width': '100vh'
        }}
        onTextChanged={onTextChanged}
        onLoad={(wrapper: MonacoEditorLanguageClientWrapper) => {
            setEditor(wrapper.getEditor());
                
            // console.log(`Loaded ${wrapper.reportStatus().join('\n').toString()}`);
        }}
        // onError={(e) => {
        //     console.error(e);
        // }}
    />;
};