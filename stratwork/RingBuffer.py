class RingBuffer:
    def __init__(self, capacity):
        self._max_capacity = capacity
        self._container = []
        self._most_recent_index = -1

    def length(self):
        return len(self._container)

    def get_capacity(self):
        return self._max_capacity
    
    def at_capacity(self):
        return len(self._container) >= self._max_capacity
    
    def add_item(self, item):
        self._most_recent_index = RingBuffer.increment(self._most_recent_index,self._max_capacity)
        if self.at_capacity():
            self._container[self._most_recent_index] = item
        else:
            self._container.append(item)

    def empty(self):
        return self._most_recent_index == -1

    def get_most_recent(self):
        if self.empty():
            return None
        return self.at(self.get_most_recent_index())

    def get_least_recent(self):
        if self.empty():
            return None
        return self.at(self.get_least_recent_index())
    
    def at(self, index):
        return self._container[index]

    def get_most_recent_index(self):
        return self._most_recent_index

    def get_least_recent_index(self):
        return RingBuffer.increment(self._most_recent_index,self._max_capacity) if self.at_capacity() else 0

    def __iter__(self):
        return RingBufferIter(self)
    
    @staticmethod 
    def increment(input, boundary):
        return (input+1)%boundary
    
    @staticmethod 
    def decrement(input, boundary):
        return (input-1)%boundary
    
class RingBufferIter:
    def __init__(self, ring_buffer: RingBuffer):
        self._buffer = ring_buffer
        self._current_index = ring_buffer.get_least_recent_index()
        self._items_processed = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self._items_processed < self._buffer.length():
            item = self._buffer.at(self._current_index)
            self._current_index = RingBuffer.increment(self._current_index, self._buffer.get_capacity())
            self._items_processed += 1
            return item
        raise StopIteration