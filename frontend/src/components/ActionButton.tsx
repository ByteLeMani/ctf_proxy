

interface ActionButtonProps {
    children: React.ReactNode;
    color: string;
    onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
}

function ActionButton({ children, color, onClick=()=>{} }: ActionButtonProps) {
    return <>
        <button className={`btn-service-logs  rounded-lg p-2 ${color}`} onClick={onClick}>
            {children}
        </button>
    </>
}

export default ActionButton