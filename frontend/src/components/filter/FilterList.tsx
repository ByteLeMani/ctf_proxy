import { useEffect, useRef, useState } from "react";
import { Filter } from "../../models/Filter";
import FilterRow from "./FilterRow";
import ActionButton from "../ActionButton";
import icons from "../../icons/icons";
import Modal from "./modals/Modal";
import Remove from "./modals/RemoveModal";

const templateItem:Filter = { id: 0, port: 3000, type: 'PostBody', pattern: '/"username": "\w{"{51,}"}"/i', isActive: true };

export default function FilterList() {
    const [items, setItems] = useState<Filter[]>([
        templateItem,
        { id: 1, port: 4000, type: 'Cookie', pattern: 'AAAAAAAAAAAAAAAAAAAA', isActive: false },
        { id: 2, port: 5000, type: 'Everywhere', pattern: 'topolino', isActive: true },
    ]);

    const [selectedItem, setSelectedItem] = useState<Filter | null>(templateItem);
    const editModal = useRef<HTMLDialogElement>(null);
    const removeModal = useRef<HTMLDialogElement>(null);
    const addModal = useRef<HTMLDialogElement>(null);

    
    useEffect(()=>{
        editModal.current?.addEventListener('close', ()=>{
            setSelectedItem(null); 
        })
        addModal.current?.addEventListener('close', ()=>{
            setSelectedItem(null); 
        })
        removeModal.current?.addEventListener('close', ()=>{
            setSelectedItem(null); 
        })
    }, [])


    const openModal = (item: Filter) => {
        setSelectedItem(item);
        editModal.current?.showModal();
        
    };

    const closeModal = () => {
        editModal.current?.close();
        setSelectedItem(null);
        
    };

    const openAddModal = () => {
        setSelectedItem(templateItem);
        addModal.current?.showModal();
    };

    const closeAddModal = () => {
        addModal.current?.close();
        setSelectedItem(null);
    };

    const openRemoveModal = (item: Filter) => {
        setSelectedItem(item);
        removeModal.current?.showModal();
    };

    const closeRemoveModal = () => {
        removeModal.current?.close();
        setSelectedItem(null);
    };

    const handleFormSubmit = (updatedItem: Filter) => {
        setItems((prevItems) =>
            prevItems.map((item) =>
                item.id === updatedItem.id ? updatedItem : item
            )
        );
        closeModal();
    };



    const handleAdd = function (newItem: Filter) {
        console.log("Total: "+ items.length + ", ADD: " + JSON.stringify(newItem, null, 2));
        setItems([...items, {...newItem, id: items[items.length-1].id+1}]);
        closeAddModal();
    }

    const handleRemove = function () {
        setItems((prevItems) => prevItems.filter((item) => item.id !== selectedItem?.id));
        closeRemoveModal()
    }



    return <>
        {/* <Pippo filter={newItem} callback={handleEdit}><p>test</p></Pippo> */}
        <div className="flex justify-between">
            <p className="text-4xl">Filters</p>
            <ActionButton color='bg-blue-400' onClick={openAddModal}><icons.Add /></ActionButton>
        </div>
        <Modal
         ref={editModal}
         filter={selectedItem}
         onClose={closeModal}
         onSubmit={handleFormSubmit}/>
        
        <Modal
         ref={addModal}
         filter={selectedItem}
         onClose={closeAddModal}
         onSubmit={handleAdd}  />
        
        <Remove ref={removeModal} handleRemove={handleRemove}/>
        
        
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
                        return <FilterRow key={item.id} filter={item} handleEdit={handleFormSubmit} openEditModal={openModal} openRemoveModal={openRemoveModal}/>
                    })}
                </tbody>
            </table>
        </div>
        </>
}