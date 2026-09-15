<?php
session_start(); // MUST be first, before any output or header()

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    header("Location: http://localhost/hackerton/index.html");
    exit();
}

$con = mysqli_connect("localhost", "root", "", "hackerton");

if (!$con) {
    die("Connection failed: " . mysqli_connect_error());
}

$username = trim($_POST['username'] ?? '');
$rawPass  = $_POST['password']     ?? '';

if (empty($username) || empty($rawPass)) {
    $con->close();
    header("Location: http://localhost/hackerton/index.html?error=Please+fill+in+all+fields.");
    exit();
}

// Fetch user by email
$stmt = $con->prepare("SELECT id, FirstName, Password FROM registration WHERE Email = ?");
$stmt->bind_param("s", $username);
$stmt->execute();
$stmt->store_result();

if ($stmt->num_rows === 1) {
    $stmt->bind_result($userId, $firstName, $hashedPassword);
    $stmt->fetch();
    $stmt->close();

    // Verify bcrypt hash
    if (password_verify($rawPass, $hashedPassword)) {
        $_SESSION['user_id']    = $userId;
        $_SESSION['user_email'] = $username;
        $_SESSION['user_name']  = $firstName;
        $con->close();
        header('Location: http://localhost/hackerton/home.html');
        exit();
    } else {
        $con->close();
        header("Location: http://localhost/hackerton/index.html?error=Invalid+email+or+password.");
        exit();
    }
} else {
    $stmt->close();
    $con->close();
    header("Location: http://localhost/hackerton/index.html?error=No+account+found+with+that+email.");
    exit();
}
?>