import './App.css'
import ActionButton from './components/ActionButton'
import Divider from './components/Divider'
import FilterList from './components/filter/FilterList'
import SericeRow from './components/ServiceRow'
import Icons from './icons/icons'

function App() {

  return (
    <>
     <div className="main w-9/12 mx-auto relative h-svh">
            <h1 className="text-6xl text-center">CTF-Proxy</h1>
            <div className="flex justify-between">
                <p className="text-4xl">Active Services</p>
                <ActionButton color='bg-blue-400' onClick={()=>{}}><Icons.Add/></ActionButton>
            </div>
            <div className="list-services mt-3 space-y-2 mb-3">
                {/* <!-- think of these as components --> */}
                 <SericeRow name='CCForms' ports='3005:3000'/>
                 <SericeRow name='CCalendar' ports='4005:4000'/>
            </div>
            <Divider/>
            <div className="flex justify-between">
                <p className="text-4xl">Filters</p>
                <ActionButton color='bg-blue-400' onClick={()=>{}}><Icons.Add/></ActionButton>
            </div>
            <FilterList/>

           <div className="flex absolute bottom-0 justify-center items-center w-full">
           <p>Copyright &#169; 2024 - Made with ❤️ by <a href='https://github.com/ByteLeMani/'>@ByteLeMani</a></p>
           </div>
        </div>

    </>
  )
}

export default App
