import ActionButton from "../ActionButton"
import icons from "../../icons/icons"
import { Filter } from "../../models/Filter";

interface FilterRowProps {
    filter: Filter;
    handleEdit: (i: Filter) => void;
    handleRemove?: () => void;
    openEditModal: (filter: Filter) => void;
    openRemoveModal: (filter: Filter) => void;
}



function FilterRow({ filter, handleEdit, openEditModal, openRemoveModal }: FilterRowProps) {
    const reducedPattern = filter.pattern.length > 30 ? filter.pattern.substring(0, 30) + "..." : filter.pattern;
    return <>
        <tr>
            <td className="border">
                <span className="rounded-lg p-2 bg-lime-500  dark:bg-lime-700">
                    {filter.port}
                </span>
            </td>
            <td className="border py-4"><p className="font-bold">{filter.type}</p></td>
            <td className="border">

                <div className="relative">
                    <code className={filter.direction?.includes("in") ? 'text-red-500 hover:text-red-700':'text-blue-500 hover:text-blue-700'}>
                        {reducedPattern}
                    </code>
                    <div className="absolute start-1 top-0">
                    {filter.direction?.includes("in") ?
                        <icons.InArrow color='text-red-500' /> : <icons.OutArrow color='text-blue-500' />}
                    </div>
                </div>
            </td>
            <td className="border">
                <input type="checkbox" defaultChecked={filter.isActive} className="checkbox" onChange={(e) => {
                    handleEdit({ ...filter, isActive: e.target.checked });
                }} /></td>

            <td className="border">
                <ActionButton
                    color="bg-yellow-400 hover:bg-yellow-500 dark:bg-yellow-700 dark:hover:bg-yellow-800"
                    onClick={() => { openEditModal(filter) }}>
                    <icons.Edit />
                </ActionButton>

            </td>

            <td className="border">
                <ActionButton
                    color="bg-red-500 hover:bg-red-500 dark:bg-red-700 dark:hover:bg-red-800"
                    onClick={() => { openRemoveModal(filter) }}>
                    <icons.Remove />
                </ActionButton>

            </td>
        </tr>
    </>
}

export default FilterRow