<?php
header("Content-Type: application/json");
header("X-Content-Type-Options: nosniff");
header("X-Frame-Options: DENY");

// Resend API Key — read from environment variable or .env file
$apiKey = getenv('RESEND_API_KEY');
if (!$apiKey) {
    $envFile = __DIR__ . '/.env';
    if (file_exists($envFile)) {
        $lines = file($envFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        foreach ($lines as $line) {
            $line = trim($line);
            if (strpos($line, 'RESEND_API_KEY=') === 0) {
                $apiKey = trim(substr($line, strlen('RESEND_API_KEY=')));
                break;
            }
        }
    }
}
if (!$apiKey) {
    http_response_code(500);
    echo json_encode(["error" => "Server configuration error: RESEND_API_KEY not set."]);
    exit;
}

// 1. Honeypot Spam Protection
// If the hidden 'website' field is filled, it's a bot submission.
// We return a fake 200 success response so the bot stops submitting, but we do NOT send the email.
if (!empty($_POST['website'])) {
    echo json_encode(["status" => "success", "message" => "Enquiry received successfully."]);
    exit;
}

// 2. Extract and Sanitize Inputs
$name = isset($_POST['name']) ? trim($_POST['name']) : '';
$email = isset($_POST['email']) ? trim($_POST['email']) : '';
$phone = isset($_POST['phone']) ? trim($_POST['phone']) : '';
$company = isset($_POST['company']) ? trim($_POST['company']) : '';
$message = isset($_POST['message']) ? trim($_POST['message']) : '';

// 3. Strict Input Validation
if (empty($name) || empty($email) || empty($message)) {
    http_response_code(400);
    echo json_encode(["error" => "Name, email, and message are required."]);
    exit;
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    echo json_encode(["error" => "Please enter a valid email address."]);
    exit;
}

// Basic phone validation (digits, space, +, -, (, ))
if (!empty($phone) && !preg_match('/^[0-9\s\+\-\(\)]+$/', $phone)) {
    http_response_code(400);
    echo json_encode(["error" => "Invalid phone number format."]);
    exit;
}

// 4. Secure Referer & Origin Checks
$allowed_hosts = ['santoshpolymers.com', 'santoshpolymers.co.in', 'localhost', '127.0.0.1'];
$request_valid = false;

// Check Origin Header
if (isset($_SERVER['HTTP_ORIGIN'])) {
    $origin = parse_url($_SERVER['HTTP_ORIGIN'], PHP_URL_HOST);
    foreach ($allowed_hosts as $host) {
        if ($origin === $host || strpos($origin, $host) !== false) {
            $request_valid = true;
            break;
        }
    }
} 
// Check Referer Header if Origin is not present
elseif (isset($_SERVER['HTTP_REFERER'])) {
    $referer = parse_url($_SERVER['HTTP_REFERER'], PHP_URL_HOST);
    foreach ($allowed_hosts as $host) {
        if ($referer === $host || strpos($referer, $host) !== false) {
            $request_valid = true;
            break;
        }
    }
}

if (!$request_valid) {
    http_response_code(403);
    echo json_encode(["error" => "Forbidden: Unauthorized request origin."]);
    exit;
}

// Escape outputs for email body
$safeName = htmlspecialchars($name, ENT_QUOTES, 'UTF-8');
$safeEmail = filter_var($email, FILTER_SANITIZE_EMAIL);
$safePhone = htmlspecialchars($phone, ENT_QUOTES, 'UTF-8');
$safeCompany = htmlspecialchars($company, ENT_QUOTES, 'UTF-8');
$safeMessage = nl2br(htmlspecialchars($message, ENT_QUOTES, 'UTF-8'));

$product_name = isset($_POST['product_name']) ? trim($_POST['product_name']) : '';
$quantity = isset($_POST['quantity']) ? trim($_POST['quantity']) : '';
$unit = isset($_POST['unit']) ? trim($_POST['unit']) : '';
$purpose = isset($_POST['purpose']) ? trim($_POST['purpose']) : '';

$safeProductName = htmlspecialchars($product_name, ENT_QUOTES, 'UTF-8');
$safeQuantity = htmlspecialchars($quantity, ENT_QUOTES, 'UTF-8');
$safeUnit = htmlspecialchars($unit, ENT_QUOTES, 'UTF-8');
$safePurpose = htmlspecialchars($purpose, ENT_QUOTES, 'UTF-8');

if (!empty($safeProductName)) {
    $subject = "Product Enquiry: " . $safeProductName . " - " . $safeName;
    $htmlContent = "<h3>New Product Enquiry Submission</h3>
                    <p><strong>Product Name:</strong> {$safeProductName}</p>
                    <p><strong>Quantity:</strong> {$safeQuantity} {$safeUnit}</p>
                    <p><strong>Purpose of Requirement:</strong> {$safePurpose}</p>
                    <hr>
                    <p><strong>Customer Name:</strong> {$safeName}</p>
                    <p><strong>Email:</strong> {$safeEmail}</p>
                    <p><strong>Phone:</strong> {$safePhone}</p>
                    <p><strong>Company:</strong> {$safeCompany}</p>
                    <p><strong>Message/Requirements:</strong><br>{$safeMessage}</p>";
} else {
    $subject = "New Contact Enquiry: " . $safeName;
    $htmlContent = "<h3>New Contact Form Submission</h3>
                    <p><strong>Name:</strong> {$safeName}</p>
                    <p><strong>Email:</strong> {$safeEmail}</p>
                    <p><strong>Phone:</strong> {$safePhone}</p>
                    <p><strong>Company:</strong> {$safeCompany}</p>
                    <p><strong>Message:</strong><br>{$safeMessage}</p>";
}

$resendData = [
    "from" => "onboarding@resend.dev",
    "to" => "santoshpolymers.info@gmail.com",
    "subject" => $subject,
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
