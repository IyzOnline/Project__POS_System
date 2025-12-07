class App():
  def __init__(self) :
    order = Order(self.someMethod)
  def someMethod(self) :
    print("Hello!")
  
class Order() :
  def __init__(self, someMethod) :
    someMethod()
    print("World!")

app = App()