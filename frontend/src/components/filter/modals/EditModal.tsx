import Form from "../FilterForm";
import { Filter } from "../../../models/Filter";

// interface EditProps {
//   type: string;
//   handleEdit: React.Dispatch<React.SetStateAction<string>>;
// }
interface EditProps {
    filter: Filter;
    setNewFilter: React.Dispatch<React.SetStateAction<Filter>>;
    handleEdit: (i?:Filter) => void;
}

export default function Edit({ filter, setNewFilter, handleEdit }: EditProps) {

    // setCurrentType(type);
    return <dialog id="edit_modal" className="modal text-start">
        <div className={`modal-box ${filter.type.includes("Custom") ? ' w-11/12 max-w-5xl' : '' }`}>
            <h3 className="text-lg font-bold text-center">Edit Filter</h3>
            <Form currentFilter={filter} setCurrentFilter={setNewFilter} handleEdit={handleEdit}>
                
            </Form>
        </div>
    </dialog>
}
