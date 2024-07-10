import { useEffect, useState } from "react";
import { Filter } from "../../models/Filter";
import FilterRow from "./FilterRow";



export default function FilterList() {
    const [items, setItems] = useState<Filter[]>([
        { port: 3000, type: 'PostBody', pattern: '/"username": "\w{"{51,}"}"/i', isActive: true},
        { port: 4000, type: 'Cookie', pattern: 'AAAAAAAAAAAAAAAAAAAA', isActive: false},
        { port: 5000, type: 'Everywhere', pattern: 'topolino', isActive: true},
    ]);

    const [currentItem, setCurrentItem] = useState<Filter>(items[0]);
    const [newItem, setNewItem] = useState<Filter>(items[0]);
    const [removePort, setRemovePort] = useState<number>(0); 


    const handleEdit = function(){
        setItems((prevItems) =>
            prevItems.map((item) =>
              item.port === currentItem.port ? newItem  : item
            )
          );
    }

    const handleRemove = function(){
        setItems((prevItems) => prevItems.filter((item) => item.port !== removePort));
    }

    
    const openEditModal = function(item:Filter){
        setCurrentItem(item);
        setNewItem(item);
        // alert(JSON.stringify(item));
        document!!.getElementById('edit_modal')!!.showModal();
    }

    const openRemoveModal = function(item:Filter){
        setCurrentItem(item);
        setRemovePort(item.port)
        document!!.getElementById('remove_modal')!!.showModal();
    }
    

    return <div className="list-filters content-center mt-3">
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
                {items.map((item:Filter) => {
                    return <FilterRow key={item.port} filter={item} openEditModal={openEditModal} openRemoveModal={openRemoveModal} handleEdit={handleEdit} handleRemove={handleRemove} newFilter={newItem} setNewFilter={setNewItem} />
                })}
            </tbody>
        </table>
    </div>
}