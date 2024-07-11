import { useState } from "react";
import Form from "./FilterForm";
import { Filter } from "../../models/Filter";

// interface EditProps {
//   type: string;
//   handleEdit: React.Dispatch<React.SetStateAction<string>>;
// }
interface EditProps {
  filter: Filter;
  setNewFilter: React.Dispatch<React.SetStateAction<Filter>>;
  handleEdit: () => void;
}

function Edit({ filter, setNewFilter, handleEdit }: EditProps) {
  
  // setCurrentType(type);
  return <dialog id="edit_modal" className="modal">
    <div className="modal-box">
      <h3 className="text-lg font-bold">Edit Filter</h3>
      <Form currentFilter={filter} setCurrentFilter={setNewFilter}>
        <form method="dialog">
          <button className="btn" onClick={handleEdit}>Confirm</button>
        </form>
      </Form>
    </div>
  </dialog>
}

interface RemoveProps {
  handleRemove: () => void;
}

function Remove({handleRemove}:RemoveProps) {
  
  return <dialog id="remove_modal" className="modal">
    <div className="modal-box">
      <h3 className="font-bold text-lg">Remove Filter</h3>
      <p className="py-4">Are you sure?</p>
      <form method="dialog">
        <button className="btn btn-error" onClick={handleRemove}>Confirm</button>
      </form>
    </div>
    <form method="dialog" className="modal-backdrop">
      <button>close</button>
    </form>
  </dialog>
}



interface AddProps {
  filter: Filter;
  handleAdd: () => void;
  setNewFilter: React.Dispatch<React.SetStateAction<Filter>>;
}

function Add({filter, handleAdd, setNewFilter}:AddProps) {
  
  return <dialog id="add_modal" className="modal">
    <div className="modal-box">
      <h3 className="text-lg font-bold">Edit Filter</h3>
      <Form currentFilter={filter} setCurrentFilter={setNewFilter}>
        <form method="dialog">
          <button className="btn" onClick={handleAdd}>Confirm</button>
        </form>
      </Form>
    </div>
  </dialog>
}

export default { Edit, Remove, Add }