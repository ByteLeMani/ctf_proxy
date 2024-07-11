import { useState } from "react";
import { Filter } from "../../models/Filter";
import FilterRow from "./FilterRow";
import ActionButton from "../ActionButton";
import icons from "../../icons/icons";
import Add from "./modals/AddModal";



export default function FilterList() {
    const [items, setItems] = useState<Filter[]>([
        { id: 0, port: 3000, type: 'PostBody', pattern: '/"username": "\w{"{51,}"}"/i', isActive: true },
        { id: 1, port: 4000, type: 'Cookie', pattern: 'AAAAAAAAAAAAAAAAAAAA', isActive: false },
        { id: 2, port: 5000, type: 'Everywhere', pattern: 'topolino', isActive: true },
    ]);

    const [currentItem, setCurrentItem] = useState<Filter>(items[0]);
    const [newItem, setNewItem] = useState<Filter>(items[0]);
    const [removeId, setRemoveId] = useState<number>(0);


    const handleEdit = function () {
        setItems((prevItems) =>
            prevItems.map((item) =>
                item.id === currentItem.id ? newItem : item
            )
        );
    }

    const handleAdd = function () {
        setItems([{...newItem, id: items[items.length-1].id+1}, ...items]);
    }

    const handleRemove = function () {
        setItems((prevItems) => prevItems.filter((item) => item.id !== removeId));
    }

    const openEditModal = function (item: Filter) {
        setCurrentItem(item);
        setNewItem(item);
        // alert(JSON.stringify(item));
        document!!.getElementById('edit_modal')!!.showModal();
    }

    const openRemoveModal = function (item: Filter) {
        setCurrentItem(item);
        setRemoveId(item.id)
        document!!.getElementById('remove_modal')!!.showModal();
    }

    const openAddModal = function (item: Filter) {
        setCurrentItem(item);
        setNewItem(item);
        // alert(JSON.stringify(item));
        document!!.getElementById('add_modal')!!.showModal();
    }


    return <>
        <div className="flex justify-between">
            <p className="text-4xl">Filters</p>
            <ActionButton color='bg-blue-400' onClick={() => {openAddModal(newItem)}}><icons.Add /></ActionButton>
        </div>
        <Add filter={newItem} setNewFilter={setNewItem} handleAdd={handleAdd}/>
        <div className="list-filters content-center mt-3">
            <table className="table-auto w-full border">
                <thead>
                    <tr>
                        <th className="border">Port</th>
                        <th className="border">Type</th>
                        <th className="border">Filter</th>
                        <th className="border">Active</th>
                        <th className="border">Edit</th>
                        <th className="border">Delete</th>
                    </tr>
                </thead>
                <tbody className="text-center">
                    {items.map((item: Filter) => {
                        return <FilterRow key={item.port} filter={item} openEditModal={openEditModal} openRemoveModal={openRemoveModal} handleEdit={handleEdit} handleRemove={handleRemove} newFilter={newItem} setNewFilter={setNewItem} />
                    })}
                </tbody>
            </table>
        </div>
        </>
}