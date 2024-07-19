import { ChangeEvent, useEffect, useState } from "react";
import { Filter } from "../../models/Filter";
import { editor } from "monaco-editor";
import { MonacoEditorReactComp } from "@typefox/monaco-editor-react";
import CodeEditor from "../code-editor/CodeEditor";
import HttpForm from "./form/HttpForm";
import Divider from "../Divider";

// var filter_types = [
//     "Standard",
//     "PostBody",
//     "Cookie",
//     "URL",
//     "Headers",
//     "Everywhere",
//     "Custom"
// ];
var filter_types = [
    "Standard",
    "Custom"
];
const listTypes = filter_types.map(filter => <option value={filter} key={filter}>{filter}</option>);

var service_ports = [
    3000,
    4000,
    5000
];
const listPorts = service_ports.map(port => <option value={port} key={port}>{port}</option>);


interface FormProps {
    filter: Filter | null;
    onSubmit: (filter: Filter) => void;
    editor?: React.Ref<MonacoEditorReactComp>;
}

// TODO: remove this after code editor fix
export interface CodeEditorState extends EventTarget {
    target: {
        name: string;
        value: string;
    }
}


export default function Form({ filter, onSubmit }: FormProps) {
    const [_editor, setEditor] = useState<editor.IStandaloneCodeEditor>();
    const [formState, setFormState] = useState<Filter | null>(filter);


    useEffect(() => {
        setFormState(filter);
    }, [filter]);


    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (formState) {
            onSubmit(formState);
        }
    };

    const handleChange = (e: ChangeEvent<HTMLSelectElement | HTMLInputElement | HTMLTextAreaElement> | CodeEditorState) => {
        const { name, value } = e.target;
        // if you see errors in your editor is just typescript intellisense not understanding stuff
        if (formState !== null) {
            setFormState((prevState) => ({
                ...prevState,
                [name]: value,
            }));
        }
    };


    return <div className="w-full flex flex-col items-center">
        <form onSubmit={handleSubmit} className="w-full flex flex-col items-center">
            <label className="form-control w-full flex flex-col max-w-xs">
                <div className="flex flex-row items-center justify-center">
                    <div className="form-control">
                        <label className="label cursor-pointer">
                            <span className="label-text mx-2">In</span>
                            <input type="radio" name="direction" value='in' className="radio checked:bg-red-500"
                            checked={formState?.direction==='in'} 
                            onChange={handleChange}/>
                        </label>
                    </div>
                    <div className="form-control">
                        <label className="label cursor-pointer">
                            <input type="radio" name="direction"  value='out' className="radio checked:bg-blue-500" 
                            checked={formState?.direction==='out'}
                            onChange={handleChange}/>
                            <span className="label-text mx-2">Out</span>
                        </label>
                    </div>
                </div>
            </label>
            <label className="form-control w-full max-w-xs">
                <div className="label">
                    <span className="label-text">Pick the service</span>
                </div>
                <select className="select select-bordered"
                    value={formState?.port}
                    name='port'
                    onChange={handleChange}>
                    <option disabled >Choose one</option>
                    {listPorts}
                </select>
                <div className="label">
                    <span className="label-text">Choose filter type</span>
                </div>
                <select className="select select-bordered"
                    value={formState?.type}
                    name='type'
                    onChange={handleChange}>
                    <option disabled >Choose one</option>
                    {listTypes}
                </select>
            </label>


            <label className="form-control w-full flex flex-col items-center">

                <div className="label">
                    <span className="label-text">Edit Pattern</span>
                </div>


                {
                    formState?.type.includes("Custom") ?

                        <CodeEditor
                            pattern={formState?.pattern}
                            setEditor={setEditor} />
                        :
                        <HttpForm setFormState={setFormState} formState={formState} handleChange={handleChange}/>
                }


            </label>
            <button className="btn btn-primary" type="submit">Confirm</button>
        </form>


    </div>
}

