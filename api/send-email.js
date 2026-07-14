export default async function handler(req, res) {
  // Only allow POST
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  // Security headers
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("X-Frame-Options", "DENY");

  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    console.error("RESEND_API_KEY is not configured");
    return res.status(500).json({ error: "Server configuration error." });
  }

  const body = req.body;

  // 1. Honeypot Spam Protection
  if (body.website && body.website.trim() !== "") {
    return res.status(200).json({ status: "success", message: "Enquiry received successfully." });
  }

  // 2. Extract inputs
  const name = (body.name || "").trim();
  const email = (body.email || "").trim();
  const phone = (body.phone || "").trim();
  const company = (body.company || "").trim();
  const message = (body.message || "").trim();
  const productName = (body.product_name || "").trim();
  const quantity = (body.quantity || "").trim();
  const unit = (body.unit || "").trim();
  const purpose = (body.purpose || "").trim();

  // 3. Input Validation
  if (!name || !email || !message) {
    return res.status(400).json({ error: "Name, email, and message are required." });
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return res.status(400).json({ error: "Please enter a valid email address." });
  }

  if (phone && !/^[0-9\s+\-()]+$/.test(phone)) {
    return res.status(400).json({ error: "Invalid phone number format." });
  }

  // 4. Origin Validation
  const allowedHosts = ["santoshpolymers.com", "santoshpolymers.co.in", "localhost", "127.0.0.1"];
  const origin = req.headers.origin || req.headers.referer || "";
  let requestValid = false;

  try {
    const hostname = new URL(origin).hostname;
    requestValid = allowedHosts.some(h => hostname === h || hostname.endsWith("." + h) || hostname.includes("vercel.app"));
  } catch {
    // Allow Vercel preview deployments
    if (origin.includes("vercel.app")) requestValid = true;
  }

  if (!requestValid && process.env.NODE_ENV === "production") {
    return res.status(403).json({ error: "Forbidden: Unauthorized request origin." });
  }

  // 5. Build email content
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

  let subject, htmlContent;

  if (productName) {
    subject = `Product Enquiry: ${esc(productName)} - ${esc(name)}`;
    htmlContent = `
      <h3>New Product Enquiry Submission</h3>
      <p><strong>Product Name:</strong> ${esc(productName)}</p>
      <p><strong>Quantity:</strong> ${esc(quantity)} ${esc(unit)}</p>
      <p><strong>Purpose of Requirement:</strong> ${esc(purpose)}</p>
      <hr>
      <p><strong>Customer Name:</strong> ${esc(name)}</p>
      <p><strong>Email:</strong> ${esc(email)}</p>
      <p><strong>Phone:</strong> ${esc(phone)}</p>
      <p><strong>Company:</strong> ${esc(company)}</p>
      <p><strong>Message/Requirements:</strong><br>${esc(message).replace(/\n/g, "<br>")}</p>
    `;
  } else {
    subject = `New Contact Enquiry: ${esc(name)}`;
    htmlContent = `
      <h3>New Contact Form Submission</h3>
      <p><strong>Name:</strong> ${esc(name)}</p>
      <p><strong>Email:</strong> ${esc(email)}</p>
      <p><strong>Phone:</strong> ${esc(phone)}</p>
      <p><strong>Company:</strong> ${esc(company)}</p>
      <p><strong>Message:</strong><br>${esc(message).replace(/\n/g, "<br>")}</p>
    `;
  }

  // 6. Send via Resend API
  try {
    const response = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        from: "onboarding@resend.dev",
        to: ["arnavgoel.nitkkr@gmail.com"],
        subject,
        html: htmlContent,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      return res.status(200).json({ status: "success", message: "Email sent successfully.", id: data.id });
    } else {
      console.error("Resend API error:", data);
      return res.status(response.status).json({ error: data.message || "Failed to send email." });
    }
  } catch (error) {
    console.error("Email send error:", error);
    return res.status(500).json({ error: "Internal server error." });
  }
}
