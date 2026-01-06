let users = [
  { id: 1, username: "admin", email: "admin@gmail.com", role: "admin", status: "active" },
  { id: 2, username: "user01", email: "user01@gmail.com", role: "user", status: "active" },
  { id: 3, username: "user02", email: "user02@gmail.com", role: "user", status: "locked" }
];

export const getUsers = () => {
  return Promise.resolve([...users]);
};

export const lockUser = (id) => {
  users = users.map(u =>
    u.id === id ? { ...u, status: "locked" } : u
  );
  return Promise.resolve();

};export const addUser = (user) => {
  users.push({
    id: Date.now(),
    status: "active",
    ...user
  });
  return Promise.resolve();
};

export const unlockUser = (id) => {
  users = users.map(u =>
    u.id === id ? { ...u, status: "active" } : u
  );
  return Promise.resolve();
};

export const deleteUser = (id) => {
  users = users.filter(u => u.id !== id);
  return Promise.resolve();
};
