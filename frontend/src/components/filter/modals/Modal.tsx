import React from "react";
import { Filter } from "../../../models/Filter";
import Form, { CodeEditorState } from "../FilterForm";

// }
interface ModalProps {
  filter: Filter | null;
  onClose: () => void;
  onSubmit: (filter: Filter) => void;
}

const Modal = React.forwardRef(({ filter, onClose, onSubmit }: ModalProps, ref) => {


  return <dialog ref={ref} className="modal">
    <div className="modal-box w-5/6 max-w-5xl">
      <h3 className="text-lg font-bold text-center">Edit Filter</h3>
      <Form onSubmit={onSubmit} filter={filter} />
    </div>
    <div className="modal-backdrop">
        <button onClick={onClose}>close</button>
    </div>
  </dialog>
});

export default Modal;
