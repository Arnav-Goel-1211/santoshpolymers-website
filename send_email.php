<?php
header("Content-Type: application/json");

// Hardcoded Resend API Key for simple cPanel deployment
$apiKey = "re_LBsn9Dh6_K4t5cMxcd4tEesXhZqaWu7mL";

// Extract data from standard POST (bypasses JSON ModSecurity rules)
$name = isset($_POST['name']) ? trim($_POST['name']) : '';
$email = isset($_POST['email']) ? trim($_POST['email']) : '';
$phone = isset($_POST['phone']) ? trim($_POST['phone']) : '';
$company = isset($_POST['company']) ? trim($_POST['company']) : '';
$message = isset($_POST['message']) ? trim($_POST['message']) : '';

// Basic validation
if (empty($name) || empty($email) || empty($message)) {
    http_response_code(400);
    echo json_encode(["error" => "Name, email, and message are required."]);
    exit;
}

// Basic referer check to reduce spam bots
if (!isset($_SERVER['HTTP_REFERER']) || strpos($_SERVER['HTTP_REFERER'], 'santoshpolymers') === false) {
    // We check for 'santoshpolymers' in referer. If it's a local test, it might fail, but for prod it's better.
    // For safety, allow localhost as well.
    if (!isset($_SERVER['HTTP_REFERER']) || (strpos($_SERVER['HTTP_REFERER'], 'santoshpolymers') === false && strpos($_SERVER['HTTP_REFERER'], 'localhost') === false && strpos($_SERVER['HTTP_REFERER'], '127.0.0.1') === false)) {
        http_response_code(403);
        echo json_encode(["error" => "Forbidden request source."]);
        exit;
    }
}

$safeName = htmlspecialchars($name);
$safeEmail = htmlspecialchars($email);
$safePhone = htmlspecialchars($phone);
$safeCompany = htmlspecialchars($company);
$safeMessage = nl2br(htmlspecialchars($message));

// Build the HTML email
$htmlContent = "<p><strong>Name:</strong> {$safeName}</p>
                <p><strong>Email:</strong> {$safeEmail}</p>
                <p><strong>Phone:</strong> {$safePhone}</p>
                <p><strong>Company:</strong> {$safeCompany}</p>
                <p><strong>Message:</strong><br>{$safeMessage}</p>";

$resendData = [
    "from" => "onboarding@resend.dev",
    "to" => "arnavgoel.nitkkr@gmail.com",
    "subject" => "New Contact Form Submission",
    "html" => $htmlContent
];

// Send via cURL to Resend API
$ch = curl_init("https://api.resend.com/emails");
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($resendData));
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    "Content-Type: application/json",
    "Authorization: Bearer " . $apiKey
]);

$response = curl_exec($ch);
$httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

if ($error) {
    http_response_code(500);
    echo json_encode(["error" => "cURL Error: " . $error]);
} else {
    http_response_code($httpcode);
    echo $response;
}
?>
