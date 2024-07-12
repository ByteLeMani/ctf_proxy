import Form from "../FilterForm";
import { Filter } from "../../../models/Filter";

// interface EditProps {
//   type: string;
//   handleEdit: React.Dispatch<React.SetStateAction<string>>;
// }
interface EditProps {
    filter: Filter;
    setNewFilter: React.Dispatch<React.SetStateAction<Filter>>;
    handleEdit: () => void;
}

export default function Edit({ filter, setNewFilter, handleEdit }: EditProps) {

    // setCurrentType(type);
    return <dialog id="edit_modal" className="modal" >
        <div className={`modal-box ${filter.type.includes("Custom")? 'w-11/12 max-w-5xl': ''}`}>
            <h3 className="text-lg font-bold text-center">Edit Filter</h3>
            <Form currentFilter={filter} setCurrentFilter={setNewFilter}>
                <form method="dialog">
                    <button className="btn" onClick={handleEdit}>Confirm</button>
                </form>
            </Form>
        </div>
    </dialog>
}
