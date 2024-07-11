import ActionButton from "./ActionButton"
import icons from "../icons/icons"
function ServiceRow({name, ports}:{name:string, ports:string}) {

    return (
        <>
            <div className="flex justify-between border p-2 rounded-lg">
                <div className="service-description flex items-center">
                    <span className="rounded-lg p-1 bg-lime-400">{ports}</span>
                    <p className="text-2xl ms-2">{name}</p>
                </div>
                <div className="btn-service flex space-x-2 items-center">
                    <ActionButton color="bg-cyan-400">
                        <icons.Open/>
                    </ActionButton>

                    <ActionButton color="bg-cyan-400">
                        <icons.Volumes/>
                    </ActionButton>

                    <ActionButton color="bg-yellow-400">
                        <icons.Edit/>
                    </ActionButton>

                    <ActionButton color="bg-red-500">
                        <icons.Remove/>
                    </ActionButton>
                </div>
            </div>
        </>
    )
}

export default ServiceRow
