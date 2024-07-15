export default function KeyValue(){
    return <div className="flex flex-row gap-4 m-auto">
        <input type="text" placeholder="key" className="input input-bordered w-full max-w-xs  grow-0" />
        <input type="text" placeholder="value" className="input input-bordered w-full max-w-xs grow" />
    </div>
}