import React, { useState, useEffect, useRef } from "react";
import { toast } from "react-toastify";
import settingsService from "../services/settings.service";
import searchService from "../services/search.service";
import { Plus, Trash2, Save, Eye, EyeOff } from "lucide-react";

const Settings = () => {
  const [siteUrls, setSiteUrls] = useState([]);
  const [newUrl, setNewUrl] = useState("");
  const [editingUrlId, setEditingUrlId] = useState(null);
  const [searches, setSearches] = useState([]);
  const [editingSearch, setEditingSearch] = useState(null);
  const [passwords, setPasswords] = useState({ old: "", new: "", confirm: "" });
  const [showPasswords, setShowPasswords] = useState({
    old: false,
    new: false,
    confirm: false,
  });
  const hasFetched = useRef(false);
  const carBrands = ["Abarth", "Alfa Romeo", "Alpine", "Aston Martin", "Audi", "BMW", "BYD", "Bentley", "CUPRA", "Cadillac",
     "Caterham", "Chevrolet", "Chrysler", "Citroen", "Corvette", "DFSK", "DR", "DS", "Dacia", "Daewoo", "Daihatsu", "Dodge", "EBRO", 
     "EVO", "FIAT", "Ferrari", "Ford", "Fornasari", "Galloper", "Honda", "Hummer", "Hyundai", "INEOS", "Infiniti", "Isuzu", "Iveco",
     "Jaecoo", "Jaguar", "Jeep", "KGM", "KIA", "KTM", "Karma", "LDV", "LYNK & CO", "Lada", "Lamborghini", "Lancia", "Land Rover", "Leapmotor",
      "Lexus", "Lotus", "MG", "MINI", "Mahindra", "Maserati", "Maxus", "Maybach", "Mazda", "McLaren", "Mercedes-Benz", "Mitsubishi", "Morgan",
      "Nissan", "Omoda", "Opel", "Peugeot", "Piaggio", "Porsche", "Renault", "Renault Trucks", "Rolls-Royce", "Rover", "SEAT", "Saab", "Santana",
      "Skoda", "SsangYong", "Subaru", "Suzuki", "TH!NK", "Tata", "Tesla", "Toyota", "VAZ", "Volkswagen", "Volvo", "Wiesmann", "smart"]; // Array of car brands
  const carModels = ["CLK", "GL", "GLE", "SL", "01", "08", "1007", "106", "107", "108", "110", "111", "112", "124 Spider", "12Cilindri",
     "147", "156", "159", "166", "2", "2008", "206", "207", "208", "214", "215", "25", "296", "296 Challenge", "3", "3.0", "300", "300 C",
     "300 M", "3008", "306", "307", "308", "311 GT", "3200 GT", "323", "350", "350Z", "360", "370Z", "4", "4.0", "4/4", "4007", "4008",
     "406", "407", "408", "45", "456", "458", "488", "4C", "5", "5.0", "500", "5008", "500L", "500X", "508", "580", "595", "6", "6.0",
     "600", "607", "612 Scaglietti", "626", "650S", "695", "7", "7.0", "718 Boxster", "718 Cayman", "718 Spyder", "75", "806", "807", 
     "812", "8C Competizione", "9", "9-3", "9-3X", "9-4X", "9-5", "911", "A1", "A1 allstreet", "A110", "A2", "A3", "A3 allstreet", "A4", "A4 Allroad"]; // Array of car models

  const fuelTypes = [
    { label: "Gasolina", value: "gasoline" },
    { label: "Diesel", value: "gasoil" },
    { label: "Eléctrico", value: "electric-hybrid" },
    { label: "Híbrido", value: "hybride" },
    { label: "Híbrido enchufable", value: "hybride_plugin" },
    { label: "Gas licuado (GPL)", value: "lpg" },
    { label: "Gas natural (CNG)", value: "cng" },
    { label: "Otros", value: "others" },
  ];

  const categroies = [
    { label: "Coches", value: "100"}
  ]
  
  useEffect(() => {
    
    if (!hasFetched.current) {
      fetchSiteUrls();
      fetchSearches();
      setNewUrl("");
      hasFetched.current = true;
    }
  }, []);

  const fetchSiteUrls = async () => {
    try {
      const response = await settingsService.getSiteUrls();
      setSiteUrls(response.data);
    } catch (error) {
      console.error("Error fetching site URLs:", error);
    }
  };

  const fetchSearches = async () => {
    try {
      const response = await searchService.getAllSearches();
      setSearches(response.data);
    } catch (error) {
      console.error("Error fetching searches:", error);
    }
  };

  const handleAddOrUpdateUrl = async () => {
    if (!newUrl.trim()) {
      toast.error("Por favor, ingresa una URL");
      return;
    }
    
    try {
      if (editingUrlId) {
        await settingsService.updateSiteUrl(editingUrlId, newUrl);
        toast.success("URL actualizada correctamente");
        setEditingUrlId(null);
      } else {
        await settingsService.addSiteUrl(newUrl);
        toast.success("URL agregada correctamente");
      }
      fetchSiteUrls(); // Fetch site URLs again to update the list
      setNewUrl(""); // Make sure to clear the input after adding/updating
    } catch (error) {
      toast.error("Error al guardar la URL");
    }
  };

  const handleDeleteUrl = async (id) => {
    try {
      await settingsService.deleteSiteUrl(id);
      toast.success("URL eliminada");
      fetchSiteUrls();
    } catch (error) {
      toast.error("Error al eliminar la URL");
    }
  };

  const parseIntOrNull = (value) => {
    const parsed = parseInt(value);
    return isNaN(parsed) ? null : parsed;
  };  

  const handleSaveSearch = async () => {
    if (newUrl.length === 0) {
      toast.error("Debes agregar al menos una URL");
      return;
    }
    const editSearchData = {
      name: editingSearch.name || "New Search",
      description: editingSearch.description || "",
      site_url: editingSearch.site_url || "", // or an array if your backend expects multiple URLs
      make: editingSearch.make || "",
      model: editingSearch.model || "",
      year_from: parseIntOrNull(editingSearch.year_from),
      year_to: parseIntOrNull(editingSearch.year_to),
      mileage_max: parseIntOrNull(editingSearch.mileage_max),
      target_price: parseIntOrNull(editingSearch.target_price),
      price_min: parseIntOrNull(editingSearch.price_min) || 0,
      price_max: parseIntOrNull(editingSearch.price_max) || 0,
      interval: parseIntOrNull(editingSearch.interval) || 24,
      keyword: editingSearch.keyword || "",
      category: parseIntOrNull(editingSearch.category),
      location: editingSearch.location || "",
      fuel_type: editingSearch.fuel_type || "",
      power: parseIntOrNull(editingSearch.power),
      seller: editingSearch.seller || "",
      is_active: editingSearch.is_active !== undefined ? editingSearch.is_active : true,
    };

    const newSearchData = {
      name: editingSearch.name || "New Search",
      description: editingSearch.description || "",
      site_url: newUrl, // or an array if your backend expects multiple URLs
      make: editingSearch.make || "",
      model: editingSearch.model || "",
      year_from: parseIntOrNull(editingSearch.year_from),
      year_to: parseIntOrNull(editingSearch.year_to),
      mileage_max: parseIntOrNull(editingSearch.mileage_max),
      target_price: parseIntOrNull(editingSearch.target_price),
      price_min: parseIntOrNull(editingSearch.price_min) || 0,
      price_max: parseIntOrNull(editingSearch.price_max) || 0,
      interval: parseIntOrNull(editingSearch.interval) || 24,
      keyword: editingSearch.keyword || "",
      category: parseIntOrNull(editingSearch.category),
      location: editingSearch.location || "",
      fuel_type: editingSearch.fuel_type || "",
      power: parseIntOrNull(editingSearch.power),
      seller: editingSearch.seller || "",
      is_active: editingSearch.is_active !== undefined ? editingSearch.is_active : true,
    };

    try {
      if (editingSearch.id) {
        await searchService.updateSearch(editingSearch.id, editSearchData);
        toast.success("Búsqueda actualizada");
      } else {
        await searchService.createSearch(newSearchData);
        toast.success("Búsqueda creada");
      }
      setEditingSearch(null);
      fetchSearches();
    } catch (error) {
      toast.error("Error al guardar la búsqueda");
    }
  };

  const handleDeleteSearch = async (id) => {
    if (!window.confirm("Are you sure you want to delete this search?")) return;

    try {
      await searchService.deleteSearch(id);
      toast.success("Búsqueda eliminada");
      fetchSearches();
    } catch (error) {
      toast.error("Error al eliminar la búsqueda");
    }
  };

  const handleChangePassword = async () => {
    if (passwords.new !== passwords.confirm) {
      toast.error("Las nuevas contraseñas no coinciden");
      return;
    }

    if (passwords.new.length < 6) {
      toast.error("La contraseña debe tener al menos 6 caracteres");
      return;
    }

    try {
      await settingsService.changePassword(passwords.old, passwords.new);
      toast.success("Contraseña cambiada correctamente");
      setPasswords({ old: "", new: "", confirm: "" });
    } catch (error) {
      toast.error("Error al cambiar la contraseña");
    }
  };
  
  
  return (
    <div data-testid="settings-page">
      {" "}
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Configuración</h1>
      {/* Site URLs */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">URLs del sitio</h2>

        <div className="flex space-x-2 mb-4">
          <input
            type="text"
            name="url-input"
            autoComplete="off"  // Add this line to prevent autofill
            value={newUrl}
            onChange={(e) => setNewUrl(e.target.value)}
            placeholder="https://example.com"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
           
          />
          <button
            onClick={handleAddOrUpdateUrl}
            data-testid="add-url-button"
            className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all"
          >
            <Plus size={20} />
            <span>{editingUrlId ? "Ahorrar" : "Agregar"}</span>
          </button>
        </div>

        <div className="space-y-2">
          {siteUrls.map((url) => (
            <div
              key={url.id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100"
              onClick={() => {
                setNewUrl(url.url);
                setEditingUrlId(url.id);
              }}
            >
              <span className="text-gray-700">{url.url}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteUrl(url.id);
                }}
                className="text-red-600 hover:text-red-800 transition-colors"
              >
                <Trash2 size={18} />
              </button>
            </div>
          ))}
        </div>
      </div>
      {/* Search Management + Scraping Settings inside modal */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">
            Búsquedas guardadas
          </h2>

          <button
            onClick={() =>
              setEditingSearch({
                name: "",
                description: "",
                make: "",
                model: "",
                year_from: "",
                year_to: "",
                mileage_max: "",
                is_active: true,
                interval: 24,
                keyword: "Coches",
                category: "100",
                target_price: 1000,
                price_min: 100,
                price_max: 1000,       
                fuel_type: "",
                power: "",
                location: "",
                seller: "",
              })
            }
            data-testid="new-search-button"
            className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all"
          >
            <Plus size={20} />
            <span>Nueva búsqueda</span>
          </button>
        </div>

        <div className="space-y-3 ">
          {searches.map((search) => (
            <div
              key={search.id}
              className="flex items-center justify-between p-4 bg-[#e6e6fa] my-2 rounded-lg"
            >
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">{search.name} : {search.site_url}</h3>
                <p className="text-sm text-gray-600">{search.description}</p>
                <div className="text-xs text-gray-500 mt-1">
                  {search.make && `Make: ${search.make} `}
                  {search.model && `| Model: ${search.model} `}
                  {search.target_price && `| Target: €${search.target_price}`}
                  {search.price_min && `| Min price: €${search.price_min}`}
                  {search.price_max && `| Max price: €${search.price_max}`}
                  {search.keyword && `| Keyword: ${search.keyword}`}
                  {search.category && `| Category: ${search.category}`}
                  {search.power &&  `| Power: ${search.power}`}
                  {search.mileage_max && `| Mileage: ${search.mileage_max}`}
                  {search.interval &&
                    `| Interval: ${search.interval} hours`}
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setEditingSearch(search)}
                  className="px-3 py-1 bg-blue-200 text-blue-600 rounded hover:bg-blue-300 transition-colors"
                >
                  Editar
                </button>
                <button
                  onClick={() => handleDeleteSearch(search.id)}
                  className="px-3 py-1 bg-red-200 text-red-600 rounded hover:bg-red-300 transition-colors"
                >
                  Borrar
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Edit Search Modal */}
        {editingSearch && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <h3 className="text-xl font-bold mb-4">
                {editingSearch.id ? `Editar búsqueda - ${editingSearch.site_url}` : `Crear nueva búsqueda - url:  ${newUrl}`}
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Scraping Fields */}

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre
                  </label>
                  <input
                    type="text"
                    value={editingSearch.name || ""}
                    onChange={(e) =>
                      setEditingSearch((prev) => ({
                        ...prev,
                        name: e.target.value,
                      }))
                    }
                    data-testid="search-name-input"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Descripción
                  </label>
                  <input
                    type="text"
                    value={editingSearch.description || ""}
                    onChange={(e) =>
                      setEditingSearch((prev) => ({
                        ...prev,
                        description: e.target.value,
                      }))
                    }
                    data-testid="search-description-input"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Intervalo de rastreo (horas)
                  </label>
                  <input
                    type="number"
                    value={editingSearch.interval || 24}
                    onChange={(e) =>
                      setEditingSearch((prev) => ({
                        ...prev,
                        interval: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Palabra clave
                  </label>
                  <input
                    type="text"
                    value={editingSearch.keyword || ""}
                    onChange={(e) =>
                      setEditingSearch((prev) => ({
                        ...prev,
                        keyword: e.target.value,
                      }))
                    }
                    placeholder="e.g., BMW, iPhone"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Categoría
                  </label>
                  <select
                    value={editingSearch.category || ""}
                    onChange={(e) => setEditingSearch(prev => ({ ...prev, category: e.target.value }))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    {categroies.map((fuel) => {
                      return (
                        <option key={fuel.value} value={fuel.value}>
                          {fuel.label}
                        </option>
                      )
                    })}
                  </select>
                  
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Precio objetivo (€)
                  </label>
                  <input
                    type="number"
                    value={editingSearch.target_price || ""}
                    onChange={(e) =>
                      setEditingSearch((prev) => ({
                        ...prev,
                        target_price: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Precio mínimo (€)
                  </label>
                  <input
                    type="number"
                    value={editingSearch.price_min || ""}
                    onChange={(e) =>
                      setEditingSearch((prev) => ({
                        ...prev,
                        price_min: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Precio máximo (€)
                  </label>
                  <input
                    type="number"
                    value={editingSearch.price_max || ""}
                    onChange={(e) =>
                      setEditingSearch((prev) => ({
                        ...prev,
                        price_max: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Marca
                  </label>
                  <select
                    value={editingSearch.make || ""}
                    onChange={(e) =>
                      setEditingSearch((prev) => ({
                        ...prev,
                        make: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value=""></option>  {/* Placeholder option */}
                    {carBrands.map((brand) => (
                      <option key={brand} value={brand}>
                        {brand}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Modelo
                  </label>
                  <select
                    value={editingSearch.model || ""}
                    onChange={(e) =>
                      setEditingSearch((prev) => ({
                        ...prev,
                        model: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value=""></option>  {/* Placeholder option */}
                    {carModels.map((model) => (
                      <option key={model} value={model}>
                        {model}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                      Combustible
                  </label>
                  <select
                    value={editingSearch.fuel_type || ""}
                    onChange={(e) => setEditingSearch(prev => ({ ...prev, fuel_type: e.target.value }))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value=""></option>
                    {fuelTypes.map((fuel) => {
                      return (
                        <option key={fuel.value} value={fuel.value}>
                          {fuel.label}
                        </option>
                      )
                    })}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Caballos(CV)
                  </label>
                  <input
                    type="number"
                    value={editingSearch.power || ""}
                    onChange={(e) =>
                      setEditingSearch((prev) => ({
                        ...prev,
                        power: e.target.value,
                      }))
                    }
                    placeholder="e.g., 120"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Año
                  </label>
                  <input
                    type="number"
                    value={editingSearch.year_from || ""}
                    onChange={(e) =>
                      setEditingSearch((prev) => ({
                        ...prev,
                        year_from: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Hasta el año
                  </label>
                  <input
                    type="number"
                    value={editingSearch.year_to || ""}
                    onChange={(e) =>
                      setEditingSearch((prev) => ({
                        ...prev,
                        year_to: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Kilometraje
                  </label>
                  <input
                    type="number"
                    value={editingSearch.mileage_max || ""}
                    onChange={(e) =>
                      setEditingSearch((prev) => ({
                        ...prev,
                        mileage_max: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Ubicación
                  </label>
                  <input
                    type="text"
                    value={editingSearch.location || ""}
                    onChange={(e) =>
                      setEditingSearch((prev) => ({
                        ...prev,
                        location: e.target.value,
                      }))
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div> */}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Tipo de vendedor</label>
                  <select
                    value={editingSearch.seller || ''}
                    onChange={(e) => setEditingSearch(prev => ({ ...prev, seller: e.target.value }))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value=""></option>
                    <option value="Paticular">Paticular</option>
                    <option value="Professional">Profesional</option>
                  </select>
                </div>

                <div className="mt-5 ml-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <input
                      type="checkbox"
                      checked={editingSearch.is_active || false}
                      onChange={(e) =>
                        setEditingSearch((prev) => ({
                          ...prev,
                          is_active: e.target.checked,
                        }))
                      }
                      className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm font-medium text-gray-700 pl-1">
                        Activa
                    </span>
                  </label>
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setEditingSearch(null)}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleSaveSearch}
                  data-testid="save-search-button"
                  className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all"
                >
                  Ahorrar
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
      {/* Change Password */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Cambiar contraseña
        </h2>

        <div className="space-y-4 max-w-md">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Contraseña actual
            </label>
            <div className="relative">
              <input
                type={showPasswords.old ? "text" : "password"}
                value={passwords.old}
                onChange={(e) =>
                  setPasswords((prev) => ({ ...prev, old: e.target.value }))
                }
                data-testid="old-password-input"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                type="button"
                onClick={() =>
                  setShowPasswords((prev) => ({ ...prev, old: !prev.old }))
                }
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400"
              >
                {showPasswords.old ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nueva contraseña
            </label>
            <div className="relative">
              <input
                type={showPasswords.new ? "text" : "password"}
                value={passwords.new}
                onChange={(e) =>
                  setPasswords((prev) => ({ ...prev, new: e.target.value }))
                }
                data-testid="new-password-input"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                type="button"
                onClick={() =>
                  setShowPasswords((prev) => ({ ...prev, new: !prev.new }))
                }
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400"
              >
                {showPasswords.new ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Confirmar nueva contraseña
            </label>
            <div className="relative">
              <input
                type={showPasswords.confirm ? "text" : "password"}
                value={passwords.confirm}
                onChange={(e) =>
                  setPasswords((prev) => ({ ...prev, confirm: e.target.value }))
                }
                data-testid="confirm-password-input"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                type="button"
                onClick={() =>
                  setShowPasswords((prev) => ({
                    ...prev,
                    confirm: !prev.confirm,
                  }))
                }
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400"
              >
                {showPasswords.confirm ? (
                  <EyeOff size={18} />
                ) : (
                  <Eye size={18} />
                )}
              </button>
            </div>
          </div>

          <button
            onClick={handleChangePassword}
            data-testid="change-password-button"
            className="flex items-center space-x-2 px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all"
          >
            <Save size={20} />
            <span>Cambiar contraseña</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
