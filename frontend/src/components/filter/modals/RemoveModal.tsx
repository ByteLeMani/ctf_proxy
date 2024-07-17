import React from "react";
import { forwardRef } from "react";

interface RemoveProps {
    handleRemove: () => void;
}

const Remove = React.forwardRef(({ handleRemove }: RemoveProps, ref) => {

    return <dialog ref={ref} id="remove_modal" className="modal">
        <div className="modal-box text-center">
            <h3 className="font-bold text-lg">Remove Filter</h3>
            <p className="py-4">Are you sure?</p>
            <button className="btn btn-error" onClick={handleRemove}>Confirm</button>
        </div>
        <form method="dialog" className="modal-backdrop">
            <button>close</button>
        </form>
    </dialog>
});

export default Remove;