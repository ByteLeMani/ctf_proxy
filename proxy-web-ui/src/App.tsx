import './App.css'
import ActionButton from './components/ActionButton'
import Divider from './components/Divider'
import FilterList from './components/filter/FilterList'
import ServiceRow from './components/ServiceRow'
import Icons from './icons/icons'



function App() {

  var serviceList = [
    {name :"CCForms", iport: 3005, oport: 3000},
    {name :"CCalendar", iport: 4005, oport: 4000}
  ]
  
  return (
    <>
     <div className="main w-9/12 mx-auto relative h-svh">
            <h1 className="text-6xl text-center">CTF-Proxy</h1>
            <div className="flex justify-between">
                <p className="text-4xl">Active Services</p>
                <ActionButton color='bg-blue-400'><Icons.Add/></ActionButton>
            </div>
            <div className="list-services mt-3 space-y-2 mb-3">
                {
                  serviceList.map((service)=>{
                    return <ServiceRow key={service.name} name={service.name} ports={`${service.iport}:${service.oport}`}/>
                  })
                }
            </div>
            <Divider/>
            
            <FilterList/>

           <div className="flex absolute bottom-2 justify-center items-center w-full">
           <p>Copyright &#169; 2024 - Made with ❤️ by <a href='https://github.com/ByteLeMani/'>@ByteLeMani</a></p>
           </div>
        </div>

    </>
  )
}

export default App
