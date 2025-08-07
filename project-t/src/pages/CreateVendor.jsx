import { useState } from "react";

const CreateVendor = () => {
  const [formData, setFormData] = useState({
    vendor_type: "",
    business_name: "",
    contact_name: "",
    mobile_number: "",
    city: "",
    summary: "",
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.id]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      const response = await fetch("http://localhost:8000/vendors", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error("Failed to add vendor");

      const data = await response.json();
      setMessage(`Vendor created with ID: ${data.id || "success"}`);
      setFormData({ name: "", email: "", phone: "", vendor_type: "" });
    } catch (err) {
      setMessage("Error adding vendor: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (<>
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-indigo-100 flex items-center justify-center p-4">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-6 md:p-8 rounded-2xl shadow-xl w-full max-w-md space-y-4"
      >
        <h2 className="text-2xl font-semibold text-center text-gray-800 mb-4">
          Create Vendor
        </h2>

     <div>
          <label
            htmlFor="vendor_type"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Vendor Type
          </label>
          <select
            id="vendor_type"
            value={formData.vendor_type}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2"
            required
          >
            <option value="">Select Vendor Type</option>
            <option value="Driver">Driver</option>
            <option value="Restaurant">Restaurant</option>
            <option value="Artwork/Craftwork">Artwork/Craftwork</option>
          </select>
        </div>

        <div>
          <label
            htmlFor="business_name"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Business Name
          </label>
          <input
            id="business_name"
            value={formData.business_name}
            onChange={handleChange}
            placeholder="e.g. Gujarat Cabs"
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>

        <div>
          <label
            htmlFor="contact_name"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Contact Name
          </label>
          <input
            id="contact_name"
            value={formData.contact_name}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>

        <div>
          <label
            htmlFor="mobile_number"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Mobile Number
          </label>
          <input
            id="mobile_number"
            value={formData.mobile_number}
            onChange={handleChange}
            type="tel"
            pattern="[0-9]{10}"
            maxLength={10}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>

        <div>
          <label
            htmlFor="city"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            City
          </label>
          <input
            id="city"
            value={formData.city}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>

        <div>
          <label
            htmlFor="summary"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Summary
          </label>
          <textarea
            id="summary"
            value={formData.summary}
            onChange={handleChange}
            placeholder="Short description of service"
            rows={1}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition duration-200"
          disabled={loading}
        >
          {loading ? "Creating..." : "Create Vendor"}
        </button>

        {message && (
          <div className="text-center text-sm mt-2 text-gray-700">
            {message}
          </div>
        )}
      </form>
    </div>
    </>
  );
};

export default CreateVendor;
