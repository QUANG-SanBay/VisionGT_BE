import React from "react";

const UserTable = ({ users, onLock, onUnlock, onDelete }) => {
  return (
    <table border="1" cellPadding="8" width="100%">
      <thead>
        <tr>
          <th>ID</th>
          <th>Tài khoản</th>
          <th>Email</th>
          <th>Quyền</th>
          <th>Trạng thái</th>
          <th>Thao tác</th>
        </tr>
      </thead>
      <tbody>
        {users.map(user => (
          <tr key={user.id}>
            <td>{user.id}</td>
            <td>{user.username}</td>
            <td>{user.email}</td>
            <td>{user.role}</td>
            <td>{user.status}</td>
            <td>
              {user.status === "active" ? (
                <button onClick={() => onLock(user.id)}>Khóa</button>
              ) : (
                <button onClick={() => onUnlock(user.id)}>Mở</button>
              )}
              {" "}
              <button onClick={() => onDelete(user.id)}>Xóa</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default UserTable;
