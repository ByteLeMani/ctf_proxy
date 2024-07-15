interface RemoveProps {
    handleRemove: () => void;
}

export default function Remove({ handleRemove }: RemoveProps) {

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
