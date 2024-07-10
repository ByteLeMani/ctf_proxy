import ActionButton from "../ActionButton"
import icons from "../../icons/icons"
import FilterModal from "./FilterModal";
import { useState } from "react";
import { Filter } from "../../models/Filter";

interface FilterRowProps{
    filter: Filter;
    newFilter: Filter;
    setNewFilter: React.Dispatch<React.SetStateAction<Filter>>;
    handleEdit: ()=>void;
    openEditModal: (filter: Filter)=>void;
    openRemoveModal: (filter: Filter)=>void;
}

function FilterRow({filter, newFilter, setNewFilter, handleEdit, openEditModal, openRemoveModal}:FilterRowProps) {
    return <>
        <tr>
            <td className="border"><span className="rounded-lg p-2 bg-lime-400">{filter.port}</span></td>
            <td className="border py-4"><p className="font-bold">{filter.type}</p></td>
            <td className="border"><code className="text-red-500 hover:text-red-700">{filter.pattern}</code></td>
            <td className="border">
            <input type="checkbox" defaultChecked={filter.isActive} className="checkbox"/></td>
            
            <td className="border">
                <ActionButton 
                    color="bg-yellow-400 hover:bg-yellow-700"
                    onClick={()=>{openEditModal(filter)}}>
                    <icons.Edit/>
                </ActionButton>
                <FilterModal.Edit filter={newFilter} setNewFilter={setNewFilter} handleEdit={handleEdit}/>
            </td>
            
            <td className="border">
                <ActionButton
                    color="bg-red-500 hover:bg-red-700"
                    onClick={()=>{openRemoveModal(filter)}}>
                    <icons.Remove/>
                </ActionButton>
                <FilterModal.Remove/>
            </td>
        </tr>
    </>
}

export default FilterRow