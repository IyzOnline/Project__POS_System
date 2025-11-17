import { useState } from 'react'

function App() {
  const [message, setMessage] = useState("No greetings yet!")

  const handleClick = async () => {
    const greetingResponse = await window.electron.sayHello()
    setMessage(greetingResponse)
  }

  return (
    <>
      <h1>Below is the greeting!</h1>
      <button onClick={handleClick}>Click to see greeting!</button>
      <p>{message}</p>
    </>
  )
}

export default App
