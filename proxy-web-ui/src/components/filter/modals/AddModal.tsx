import Form from "../FilterForm";
import { Filter } from "../../../models/Filter";

interface AddProps {
    filter: Filter;
    handleAdd: () => void;
    setNewFilter: React.Dispatch<React.SetStateAction<Filter>>;
}

export default function Add({ filter, handleAdd, setNewFilter }: AddProps) {
    return <dialog id="add_modal" className="modal">
        <div className="modal-box  w-11/12 max-w-5xl">
            <h3 className="text-lg font-bold text-center">Create Filter</h3>
            <Form currentFilter={filter} setCurrentFilter={setNewFilter}>
                <form method="dialog">
                    <button className="btn" onClick={handleAdd}>Confirm</button>
                </form>
            </Form>
        </div>
    </dialog>
}
