import ActionButton from "../ActionButton"
import icons from "../../icons/icons"
import { Filter } from "../../models/Filter";

interface FilterRowProps{
    filter: Filter;
    handleEdit: (i:Filter)=>void;
    handleRemove?: ()=>void;
    openEditModal: (filter: Filter)=>void;
    openRemoveModal: (filter: Filter)=>void;
}



function FilterRow({filter, handleEdit, openEditModal, openRemoveModal}:FilterRowProps) {
    const reducedPattern = filter.pattern.length > 30 ? filter.pattern.substring(0, 30) + "...": filter.pattern;
    return <>
        <tr>
            <td className="border"><span className="rounded-lg p-2 bg-lime-400">{filter.port}</span></td>
            <td className="border py-4"><p className="font-bold">{filter.type}</p></td>
            <td className="border"><code className="text-red-500 hover:text-red-700">{reducedPattern}</code></td>
            <td className="border">
            <input type="checkbox" defaultChecked={filter.isActive} className="checkbox" onChange={(e)=>{
                handleEdit({...filter, isActive:e.target.checked});
            }}/></td>
            
            <td className="border">
                <ActionButton 
                    color="bg-yellow-400 hover:bg-yellow-700"
                    onClick={()=>{openEditModal(filter)}}>
                    <icons.Edit/>
                </ActionButton>
                
            </td>
            
            <td className="border">
                <ActionButton
                    color="bg-red-500 hover:bg-red-700"
                    onClick={()=>{openRemoveModal(filter)}}>
                    <icons.Remove/>
                </ActionButton>
                
            </td>
        </tr>
    </>
}

export default FilterRow