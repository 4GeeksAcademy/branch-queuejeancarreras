# Nota de diseño

`BranchQueue` mantiene una `deque` independiente para cada tipo de servicio. Así,
`call_next` retira el primer ticket de la cola correspondiente en O(1), sin
recorrer los clientes de otros servicios. Una cola compartida exigiría buscar y
eliminar el primer ticket del tipo solicitado, trabajo que crece con el número
de clientes en espera.

Cada cola tiene su propio bloqueo. Si dos agentes del mismo servicio llaman a la
vez, el bloqueo hace indivisible la comprobación de que hay tickets y el
`popleft`: el ticket se elimina de la cola antes de devolverlo al agente, por
lo que la segunda llamada recibe al siguiente cliente y nunca el mismo. Los
bloqueos independientes permiten que agentes de servicios distintos avancen
sin bloquearse entre sí. La emisión también protege el contador global y la
inserción para preservar la numeración y el orden de llegada.