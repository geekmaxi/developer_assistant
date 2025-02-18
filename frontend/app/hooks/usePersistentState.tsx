import { useState, useEffect } from 'react';

type SetStateAction<S> = S | ((prevState: S) => S);
type StorageHandler<T> = [T, (value: SetStateAction<T>) => void];

const usePersistentState = <T,>(
  key: string,
  defaultValue: T
): StorageHandler<T> => {
  const [state, setState] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error('Error reading localStorage:', error);
      return defaultValue;
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(state));
    } catch (error) {
      console.error('Error writing to localStorage:', error);
    }
  }, [key, state]);

  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key) {
        try {
          setState(e.newValue ? JSON.parse(e.newValue) : defaultValue);
        } catch (error) {
          console.error('Error parsing storage event:', error);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [defaultValue, key]);

  return [state, setState];
};

export default usePersistentState;