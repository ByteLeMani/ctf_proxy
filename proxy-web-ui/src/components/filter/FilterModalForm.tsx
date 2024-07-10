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


interface FormProps{
    currentFilter: Filter;
    setCurrentFilter: React.Dispatch<React.SetStateAction<Filter>>;
    children: React.ReactNode;
}
export default function Form(props:FormProps) {
    
    return <div className="flex justify-center">
        <label className="form-control w-full max-w-xs">
            <div className="label">
                <span className="label-text">Choose filter type</span>
            </div>
            <select className="select select-bordered" 
             onChange={(e)=>{
                // alert(JSON.stringify(props.currentFilter));
                props.setCurrentFilter({ ...props.currentFilter, type: e.target.value })
                
            }}>
                <option disabled >Choose one</option>
                {listTypes}
            </select>
            {props.children}
        </label>
    </div>
}

