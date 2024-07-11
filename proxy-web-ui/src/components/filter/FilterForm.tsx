import { useState } from "react";
import { Filter } from "../../models/Filter";
import CodeEditor from "../code-editor/CodeEditor";
var filter_types = [
    "PostBody",
    "Cookie",
    "URL",
    "Headers",
    "Everywhere",
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
    currentFilter: Filter;
    setCurrentFilter: React.Dispatch<React.SetStateAction<Filter>>;
    children: React.ReactNode;
}
export default function Form(props: FormProps) {
    const [isCustom, setIsCustom] = useState<Boolean>(false);

    return <div className="w-full flex flex-col items-center">
        <label className="form-control w-full max-w-xs">
            <div className="label">
                <span className="label-text">Pick the service</span>
            </div>
            <select className="select select-bordered"
                value={props.currentFilter.port}
                onChange={(e) => {
                    props.setCurrentFilter({ ...props.currentFilter, port: parseInt(e.target.value) })

                }}>
                <option disabled >Choose one</option>
                {listPorts}
            </select>
            <div className="label">
                <span className="label-text">Choose filter type</span>
            </div>
            <select className="select select-bordered"
                value={props.currentFilter.type}
                onChange={(e) => {
                    setIsCustom(e.target.value.includes("Custom"))
                    props.setCurrentFilter({ ...props.currentFilter, type: e.target.value })

                }}>
                <option disabled >Choose one</option>
                {listTypes}
            </select>
        </label>

        <label className="form-control w-full flex flex-col items-center">

            <div className="label">
                <span className="label-text">Edit pattern</span>
            </div>

            {isCustom ?
                <CodeEditor currentFilter={props.currentFilter} setCurrentFilter={props.setCurrentFilter}/> :
                <textarea className="textarea textarea-bordered h-24" placeholder="Type here the pattern..." value={props.currentFilter.pattern} onChange={(e) => { props.setCurrentFilter({ ...props.currentFilter, pattern: e.target.value }) }}>
                </textarea>
            }
            <label className="label cursor-pointer flex gap-4">
                <span className="label-text">Is regex?</span>
                <input type="checkbox" defaultChecked className="checkbox" />
            </label>

            {props.children}
        </label>
    </div>
}

