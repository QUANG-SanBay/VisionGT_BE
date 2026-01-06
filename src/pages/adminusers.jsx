import React, { useEffect, useState } from "react";
import UserTable from "../components/usertable";
import { getUsers, lockUser, unlockUser, deleteUser } from "../api/user";

const AdminUsers = () => {
  const [users, setUsers] = useState([]);

  const loadUsers = async () => {
    const data = await getUsers();
    setUsers(data);
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleLock = async (id) => {
    await lockUser(id);
    loadUsers();
  };

  const handleUnlock = async (id) => {
    await unlockUser(id);
    loadUsers();
  };

  const handleDelete = async (id) => {
    if (window.confirm("Bạn có chắc muốn xóa người dùng này?")) {
      await deleteUser(id);
      loadUsers();
    }
  };

  return (
    <div>
      <h2>QUẢN LÝ NGƯỜI DÙNG</h2>
      <UserTable
        users={users}
        onLock={handleLock}
        onUnlock={handleUnlock}
        onDelete={handleDelete}
      />
    </div>
  );
};

export default AdminUsers;
