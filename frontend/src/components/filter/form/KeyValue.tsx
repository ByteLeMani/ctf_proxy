import { ChangeEvent, ChangeEventHandler, useEffect, useRef, useState } from "react";

// export default function KeyValue({ key, value, onChange }: { key: number, value: string, onChange: (e: ChangeEventHandler) => void }) {
//     return <div className="flex flex-row gap-4 m-auto">
//         <input name="key" type="text" placeholder="key" className="input input-bordered w-full max-w-xs  grow-0" value={key} onChange={onChange} />
//         <input name="value" type="text" placeholder="value" className="input input-bordered w-full max-w-xs grow" value={value}
//             onChange={onChange} />
//     </div>
// }


interface InputField {
    id: number;
    key: string;
    value: string;
}
export const DynamicForm: React.FC = () => {
    const [inputFields, setInputFields] = useState<InputField[]>([
        { id: 1, key: '', value: '' },
    ]);

    const nextId = useRef(2);

    const handleValueChange = (id: number, value: string) => {
        setInputFields((prevFields) =>
            prevFields.map((field) =>
                field.id === id ? { ...field, value: value } : field
            )
        );
    };
    const handleKeyChange = (id: number, key: string) => {
        setInputFields((prevFields) =>
            prevFields.map((field) =>
                field.id === id ? { ...field, key: key } : field
            )
        );
    };



    useEffect(() => {
        const lastField = inputFields[inputFields.length-1]
        const shouldAddNewField = lastField.value !== '' && lastField.key !== '';

        if (shouldAddNewField) {
            setInputFields((prevFields) => [
                ...prevFields,
                { id: nextId.current++, value: '', key: '' },
            ]);
        } else{
            const nonEmptyFields = inputFields.filter((field, index) =>
                (field.value !== '' || field.key !== '') || index === inputFields.length - 1
              );
        
              if (nonEmptyFields.length !== inputFields.length) {
                setInputFields(nonEmptyFields);
              }
        }
    }, [inputFields]);

    return (
        <>
            {inputFields.map((field) => (
                <div className="flex flex-row gap-4 m-auto" key={field.id}>
                    <input
                        name="key"
                        type="text"
                        placeholder="key"
                        className="input input-bordered  max-w-xs grow-0"
                        value={field.key}
                        onChange={(e) => handleKeyChange(field.id, e.target.value)} />

                    <input
                        name="value"
                        type="text"
                        placeholder="value"
                        className="input input-bordered w-full grow"
                        value={field.value}
                        onChange={(e) => handleValueChange(field.id, e.target.value)} />
                </div>
            ))}
        </>
    );
};
