import { ChangeEvent, Dispatch, SetStateAction } from "react";
import { Filter } from "../../../models/Filter";
import { DynamicForm } from "./KeyValue";
import { CodeEditorState } from "../FilterForm";


var http_methods = [
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "PATCH",
    "HEAD",
    "OPTIONS",
    "CONNECT",
    "TRACE"
];

const listMethods = http_methods.map(port => <option value={port} key={port}>{port}</option>);

interface HttpFormProps{
    formState: Filter | null, 
    setFormState: React.Dispatch<SetStateAction<Filter | null>>;
    handleChange: (e: ChangeEvent<HTMLSelectElement | HTMLInputElement | HTMLTextAreaElement> | CodeEditorState)=>void
}

export default function HttpForm({formState, setFormState, handleChange}:HttpFormProps) {
    return (<div className="w-2/3 mb-5">
        <div className="join join-vertical w-full">
            <div className="collapse collapse-arrow join-item border-base-300 border">
                <input type="radio" name="my-accordion-4" />
                <div className="collapse-title text-xl font-medium">Method</div>
                <div className="collapse-content">
                    <select className="select select-bordered text-center w-full m-auto">
                        <option disabled >Choose one</option>
                        {listMethods}
                    </select>
                </div>
            </div>
            <div className="collapse collapse-arrow join-item border-base-300 border">
                <input type="radio" name="my-accordion-4" defaultChecked/>
                <div className="collapse-title text-xl font-medium">Body</div>
                <div className="collapse-content">
                    <textarea className="textarea textarea-bordered h-48 w-full text-base" placeholder="Type here the pattern..."
                        value={formState?.pattern}
                        onChange={handleChange}
                        name='pattern' >
                    </textarea>
                </div>
            </div>
            <div className="collapse collapse-arrow join-item border-base-300 border">
                <input type="radio" name="my-accordion-4" />
                <div className="collapse-title text-xl font-medium">Params</div>
                <div className="collapse-content">
                    <DynamicForm />
                </div>
            </div>
        </div>

    </div>)
}