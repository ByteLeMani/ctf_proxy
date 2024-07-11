import { Filter } from "../../models/Filter";

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
export default function FormEdit(props: FormProps) {

    return <div className="flex justify-center">
        <label className="form-control w-full max-w-xs">
            <div className="label">
                <span className="label-text">Pick the service</span>
            </div>
            <select className="select select-bordered"
                value={props.currentFilter.port}
                onChange={(e) => {
                    // alert(JSON.stringify(props.currentFilter));
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
                    // alert(JSON.stringify(props.currentFilter));
                    props.setCurrentFilter({ ...props.currentFilter, type: e.target.value })

                }}>
                <option disabled >Choose one</option>
                {listTypes}
            </select>

            <div className="label">
                <span className="label-text">Edit pattern</span>
            </div>
            <textarea className="textarea textarea-bordered h-24" placeholder="Type here the pattern..." value={props.currentFilter.pattern} onChange={(e) => { props.setCurrentFilter({ ...props.currentFilter, pattern: e.target.value }) }}>
            </textarea>

            {props.children}
        </label>
    </div>
}

