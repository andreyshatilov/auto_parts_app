function setupEventListeners() {
    let lastDecodedVin = '';
    clientVinInput.addEventListener('input', async (e) => {
        let val = e.target.value.replace(/\s+/g, '').toUpperCase();
        e.target.value = val;
        clientVinCounter.textContent = `${val.length}/17`;

        if (val.length === 17 && val !== lastDecodedVin) {
            lastDecodedVin = val;
            try {
                const res = await fetch(`${API_BASE_URL}/vin/decode?vin=${val}`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.is_decoded && data.brand) {
                        const brandSelect = document.getElementById('clientBrandSelect');
                        const modelSelect = document.getElementById('clientModelSelect');

                        let rawBrand = (data.brand || '').trim();
                        let brandFound = null;

                        if (rawBrand) {
                            brandFound = Array.from(brandSelect.options).find(opt => opt.value.toUpperCase() === rawBrand.toUpperCase());
                            if (!brandFound) {
                                brandFound = Array.from(brandSelect.options).find(opt => 
                                    opt.value.toUpperCase().includes(rawBrand.toUpperCase()) || 
                                    rawBrand.toUpperCase().includes(opt.value.toUpperCase())
                                );
                            }
                        }

                        if (brandFound && brandFound.value !== '__custom__') {
                            brandSelect.value = brandFound.value;
                        } else {
                            brandSelect.value = '__custom__';
                        }
                        brandSelect.onchange();
                        if (brandSelect.value === '__custom__') {
                            document.getElementById('clientCustomBrandInput').value = rawBrand;
                        }

                        let rawModel = (data.model || '').trim();
                        if (rawModel) {
                            let modelFound = null;
                            const opts = Array.from(modelSelect.options).filter(o => o.value && o.value !== '__custom__');
                            
                            modelFound = opts.find(opt => opt.value.toUpperCase() === rawModel.toUpperCase());
                            if (!modelFound) {
                                modelFound = opts.find(opt => 
                                    rawModel.toUpperCase().includes(opt.value.toUpperCase()) || 
                                    opt.value.toUpperCase().includes(rawModel.toUpperCase())
                                );
                            }

                            if (modelFound) {
                                modelSelect.value = modelFound.value;
                                modelSelect.onchange();
                            } else {
                                modelSelect.value = '__custom__';
                                modelSelect.onchange();
                                document.getElementById('clientCustomModelInput').value = rawModel;
                            }
                        }

                        if (data.release_year) {
                            const yearSelect = document.getElementById('clientYearSelect');
                            if (yearSelect) yearSelect.value = data.release_year;
                        }

                        if (data.body_type) {
                            const bodySelect = document.getElementById('clientBodySelect');
                            if (bodySelect) bodySelect.value = data.body_type;
                        }

                        if (data.engine) {
                            document.getElementById('clientEngineInput').value = data.engine;
                        }

                        if (data.fuel) {
                            const fuelSelect = document.getElementById('clientFuelSelect');
                            if (fuelSelect) fuelSelect.value = data.fuel;
                        }

                        if (data.transmission) {
                            const transSelect = document.getElementById('clientTransInput');
                            if (transSelect) transSelect.value = data.transmission;
                        }

                        showToast(` ${data.brand} ${data.model || ''} ${data.release_year ? '(' + data.release_year + ')' : ''} ╤А╨╛╨╖╨┐╤Ц╨╖╨╜╨░╨╜╨╛ ╨╖╨░ VIN!`);
                    }
                }
            } catch (err) {
                console.error(err);
            }
        }
    });

    const addVinInputEl = document.getElementById('addVinInput');
    if (addVinInputEl) {
        let modalDecodedVin = '';
        addVinInputEl.addEventListener('input', async (e) => {
            let val = e.target.value.replace(/\s+/g, '').toUpperCase();
            e.target.value = val;
            document.getElementById('addVinCounter').textContent = `${val.length}/17`;

            if (val.length === 17 && val !== modalDecodedVin) {
                modalDecodedVin = val;
                try {
                    const res = await fetch(`${API_BASE_URL}/vin/decode?vin=${val}`);
                    if (res.ok) {
                        const data = await res.json();
                        if (data.is_decoded && data.brand) {
                            showToast(` ${data.brand} ${data.model || ''} (${data.release_year || ''}) ╤А╨╛╨╖╨┐╤Ц╨╖╨╜╨░╨╜╨╛ ╨╖╨░ VIN!`);
                        }
                    }
                } catch (err) {}
            }
        });
    }

    const addVinFormEl = document.getElementById('addVinForm');
    if (addVinFormEl) {
        addVinFormEl.addEventListener('submit', async (e) => {
            e.preventDefault();
            const carId = document.getElementById('addVinCarId').value;
            const newVin = document.getElementById('addVinInput').value.trim();
            const token = localStorage.getItem(TOKEN_STORAGE_KEY);

            if (newVin.length !== 17) {
                showToast(' VIN-╨║╨╛╨┤ ╨┐╨╛╨▓╨╕╨╜╨╡╨╜ ╨╝╤Ц╤Б╤В╨╕╤В╨╕ ╤А╨╛╨▓╨╜╨╛ 17 ╤Б╨╕╨╝╨▓╨╛╨╗╤Ц╨▓!', 'error');
                return;
            }

            try {
                const decodeRes = await fetch(`${API_BASE_URL}/vin/decode?vin=${newVin}`);
                let updatePayload = { vin: newVin };
                if (decodeRes.ok) {
                    const decoded = await decodeRes.json();
                    if (decoded.brand) updatePayload.brand = decoded.brand;
                    if (decoded.model) updatePayload.model = decoded.model;
                    if (decoded.release_year) updatePayload.release_date = decoded.release_year;
                    if (decoded.engine) updatePayload.engine_code = decoded.engine;
                    if (decoded.transmission) updatePayload.transmission_type = decoded.transmission;
                }

                const res = await fetch(`${API_BASE_URL}/cars/${carId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                    body: JSON.stringify(updatePayload)
                });
                const car = await res.json();
                if (!res.ok) throw new Error(car.detail || '╨Я╨╛╨╝╨╕╨╗╨║╨░ ╨╛╨╜╨╛╨▓╨╗╨╡╨╜╨╜╤П VIN');

                showToast(` VIN-╨║╨╛╨┤ ╨╖╨▒╨╡╤А╨╡╨╢╨╡╨╜╨╛! ╨Т╤Ц╨┤╨║╤А╨╕╤В╨╛ ╨┤╨╛╤Б╤В╤Г╨┐ ╨┤╨╛ ╨б╨╡╤А╨▓╤Ц╤Б╨╜╨╛╨│╨╛ ╨С╨╛╤А╤В╨╢╤Г╤А╨╜╨░╨╗╤Г ╤В╨░ ╨в╨Ю ╨┤╨╗╤П ${car.brand} ${car.model}!`);
                closeVinRecommendationModal();
                await refreshGarage(token);
            } catch (err) {
                showToast(` ${err.message}`, 'error');
            }
        });
    }

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
            first_name: document.getElementById('regFirstName').value.trim(),
            last_name: document.getElementById('regLastName').value.trim(),
            phone: document.getElementById('regPhone').value.trim(),
            has_messenger: document.getElementById('regHasMessenger').checked
        };
        try {
            const res = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || '╨Я╨╛╨╝╨╕╨╗╨║╨░');

            localStorage.setItem(TOKEN_STORAGE_KEY, data.auth_token);
            currentClient = data.client;
            showToast(` ╨Ы╨░╤Б╨║╨░╨▓╨╛ ╨┐╤А╨╛╤Б╨╕╨╝╨╛, ${currentClient.first_name}!`);
            showMainScreen(currentClient);
        } catch (err) {
            showToast(` ${err.message}`, 'error');
        }
    });

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const phone = document.getElementById('loginPhone').value.trim();
        try {
            const res = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone })
            });
            let data = null;
            const text = await res.text();
            try { data = JSON.parse(text); } catch (_) {}

            if (!res.ok) {
                const errMsg = (data && data.detail) ? data.detail : (text || `╨Я╨╛╨╝╨╕╨╗╨║╨░ ╤Б╨╡╤А╨▓╨╡╤А╨░ (HTTP ${res.status})`);
                throw new Error(errMsg);
            }

            localStorage.setItem(TOKEN_STORAGE_KEY, data.auth_token);
            currentClient = data.client;
            showToast(`╨Ч ╨┐╨╛╨▓╨╡╤А╨╜╨╡╨╜╨╜╤П╨╝, ${currentClient.first_name}!`);
            showMainScreen(currentClient);
        } catch (err) {
            showToast(` ${err.message}`, 'error');
        }
    });

    claimPinForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const pinCode = document.getElementById('pinInput').value.trim();
        const token = localStorage.getItem(TOKEN_STORAGE_KEY);
        try {
            const res = await fetch(`${API_BASE_URL}/transfers/claim`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                body: JSON.stringify({ pin_code: pinCode })
            });
            const car = await res.json();
            if (!res.ok) throw new Error(car.detail || '╨Я╨╛╨╝╨╕╨╗╨║╨░ ╨┐╤А╨╕╨╣╨╛╨╝╤Г ╨░╨▓╤В╨╛');

            showToast(` ╨Т╤Ц╤В╨░╤Ф╨╝╨╛! ╨Р╨▓╤В╨╛╨╝╨╛╨▒╤Ц╨╗╤М ${car.brand} ${car.model} ╤В╨░ ╨▓╤Б╤П ╨╣╨╛╨│╨╛ ╤Ц╤Б╤В╨╛╤А╤Ц╤П ╨┐╤А╨╕╨╣╨╜╤П╤В╤Ц ╤Г ╨▓╨░╤И ╨│╨░╤А╨░╨╢!`);
            document.getElementById('pinInput').value = '';
            await refreshGarage(token);
        } catch (err) {
            showToast(` ${err.message}`, 'error');
        }
    });

    addGarageCarForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const token = localStorage.getItem(TOKEN_STORAGE_KEY);

        const selectedBrand = document.getElementById('clientBrandSelect').value;
        const selectedModel = document.getElementById('clientModelSelect').value;

        const finalBrand = (selectedBrand === '__custom__') 
            ? document.getElementById('clientCustomBrandInput').value.trim() 
            : selectedBrand;
            
        const finalModel = (selectedModel === '__custom__') 
            ? document.getElementById('clientCustomModelInput').value.trim() 
            : selectedModel;

        if (!finalBrand || !finalModel) {
            showToast(' ╨С╤Г╨┤╤М ╨╗╨░╤Б╨║╨░, ╨╛╨▒╨╡╤А╤Ц╤В╤М ╨░╨▒╨╛ ╨▓╨║╨░╨╢╤Ц╤В╤М ╨╝╨░╤А╨║╤Г ╤В╨░ ╨╝╨╛╨┤╨╡╨╗╤М ╨░╨▓╤В╨╛!', 'error');
            return;
        }

        let vinValue = clientVinInput.value.trim().toUpperCase();
        if (!vinValue) {
            vinValue = 'NOVIN-' + Math.random().toString(36).substring(2, 11).toUpperCase();
        } else if (vinValue.length !== 17) {
            showToast(' VIN-╨║╨╛╨┤ ╨┐╨╛╨▓╨╕╨╜╨╡╨╜ ╨╝╤Ц╤Б╤В╨╕╤В╨╕ ╤А╨╛╨▓╨╜╨╛ 17 ╤Б╨╕╨╝╨▓╨╛╨╗╤Ц╨▓ (╨░╨▒╨╛ ╨╖╨░╨╗╨╕╤И╤В╨╡ ╨┐╨╛╤А╨╛╨╢╨╜╤Ц╨╝)!', 'error');
            return;
        } else if (/^\d+$/.test(vinValue)) {
            showToast(' VIN-╨║╨╛╨┤ ╨╜╨╡ ╨╝╨╛╨╢╨╡ ╤Б╨║╨╗╨░╨┤╨░╤В╨╕╤Б╤П ╨╗╨╕╤И╨╡ ╨╖ ╤Ж╨╕╤Д╤А! ╨Т╨▓╨╡╨┤╤Ц╤В╤М ╨╝╤Ц╨╢╨╜╨░╤А╨╛╨┤╨╜╨╕╨╣ VIN (╨╜╨░╨┐╤А., WBA33AY05NFP12345)', 'error');
            return;
        }

        const fuelVal = document.getElementById('clientFuelSelect')?.value || '';
        let engineVal = document.getElementById('clientEngineInput').value.trim();
        if (fuelVal) {
            engineVal = engineVal ? `${engineVal} (${fuelVal})` : fuelVal;
        }

        const bodyVal = document.getElementById('clientBodySelect')?.value || '';
        const genVal = document.getElementById('clientGenInput')?.value.trim() || '';
        const restyleVal = document.getElementById('clientRestyleSelect')?.value || '';

        const modParts = [];
        if (bodyVal) modParts.push(bodyVal);
        if (genVal) modParts.push(`╨Я╨╛╨║╨╛╨╗╤Ц╨╜╨╜╤П: ${genVal}`);
        if (restyleVal) modParts.push(restyleVal);
        const modificationStr = modParts.length > 0 ? modParts.join(' | ') : null;

        const mileageRaw = document.getElementById('clientMileageInput')?.value.trim();
        const mileageVal = mileageRaw ? parseInt(mileageRaw) : 120000;

        const carData = {
            vin: vinValue,
            brand: finalBrand,
            model: finalModel,
            modification: modificationStr,
            release_date: document.getElementById('clientYearSelect')?.value || null,
            engine_code: engineVal || null,
            transmission_type: document.getElementById('clientTransInput').value || null,
            mileage: mileageVal
        };
        try {
            const res = await fetch(`${API_BASE_URL}/clients/me/cars`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                body: JSON.stringify(carData)
            });
            const data = await res.json();
            if (!res.ok) {
                let errMsg = '╨Я╨╛╨╝╨╕╨╗╨║╨░ ╨┤╨╛╨┤╨░╨▓╨░╨╜╨╜╤П ╨░╨▓╤В╨╛';
                if (typeof data.detail === 'string') errMsg = data.detail;
                else if (Array.isArray(data.detail)) errMsg = data.detail.map(d => d.msg || d.detail).join(', ');
                else if (data.detail && typeof data.detail === 'object') errMsg = JSON.stringify(data.detail);
                throw new Error(errMsg);
            }

            showToast(` ${data.brand} ${data.model} ╨┤╨╛╨┤╨░╨╜╨╛ ╤Г ╨▓╨░╤И ╨У╨░╤А╨░╨╢!`);
            addGarageCarForm.reset();
            initBrandAndModelSelects();
            clientVinCounter.textContent = '0/17';
            closeAddNewCarModal();
            await refreshGarage(token);

            if (vinValue.startsWith('NOVIN-')) {
                openVinRecommendationModal(data.id, `${data.brand} ${data.model}`);
            }
        } catch (err) {
            let errMsg = '╨Я╨╛╨╝╨╕╨╗╨║╨░ ╨┤╨╛╨┤╨░╨▓╨░╨╜╨╜╤П ╨░╨▓╤В╨╛';
            if (typeof err === 'string') errMsg = err;
            else if (err && err.message && typeof err.message === 'string') errMsg = err.message;
            else if (err && typeof err === 'object') {
                try { errMsg = JSON.stringify(err); } catch(e) {}
            }
            showToast(` ${errMsg}`, 'error');
        }
    });

    requestForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const token = localStorage.getItem(TOKEN_STORAGE_KEY);
        const carId = parseInt(requestCarSelect.value);
        const text = document.getElementById('requestText').value.trim();

        if (!carId) {
            showToast(' ╨Ю╨▒╨╡╤А╤Ц╤В╤М ╨░╨▓╤В╨╛ ╨╖ ╨│╨░╤А╨░╨╢╨░!', 'error');
            return;
        }

        try {
            const res = await fetch(`${API_BASE_URL}/requests/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                body: JSON.stringify({ car_id: carId, client_message: text })
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || '╨Я╨╛╨╝╨╕╨╗╨║╨░ ╨╜╨░╨┤╤Б╨╕╨╗╨░╨╜╨╜╤П');

            showToast(' ╨Ч╨░╨┐╨╕╤В ╨╜╨░ ╨┐╤Ц╨┤╨▒╤Ц╤А ╨╜╨░╨┤╤Ц╤Б╨╗╨░╨╜╨╛ ╨╡╨║╤Б╨┐╨╡╤А╤В╤Г!');
            document.getElementById('requestText').value = '';
            await loadMyRequests(token);
        } catch (err) {
            showToast(` ${err.message}`, 'error');
        }
    });

    returnForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!activeReturnOrderId) return;
        const token = localStorage.getItem(TOKEN_STORAGE_KEY);
        const reason = document.getElementById('returnReasonText').value.trim();

        try {
            const res = await fetch(`${API_BASE_URL}/returns/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                body: JSON.stringify({ order_id: activeReturnOrderId, reason })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || '╨Я╨╛╨╝╨╕╨╗╨║╨░');

            showToast(' ╨Ч╨░╤П╨▓╨║╨░ ╨╜╨░ ╨┐╨╛╨▓╨╡╤А╨╜╨╡╨╜╨╜╤П ╤В╨╛╨▓╨░╤А╤Г ╨╜╨░╨┤╤Ц╤Б╨╗╨░╨╜╨░!');
            closeReturnModal();
            await loadMyOrders(token);
        } catch (err) {
            showToast(` ${err.message}`, 'error');
        }
    });

    chatSendForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!activeChatRequestId) return;
        const token = localStorage.getItem(TOKEN_STORAGE_KEY);
        const msg = document.getElementById('chatInput').value.trim();

        try {
            const res = await fetch(`${API_BASE_URL}/chat/messages?sender_type=client`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                body: JSON.stringify({ request_id: activeChatRequestId, message: msg })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || '╨Я╨╛╨╝╨╕╨╗╨║╨░');

            document.getElementById('chatInput').value = '';
            await loadChatMessages(activeChatRequestId);
        } catch (err) {
            showToast(err.message, 'error');
        }
    });

    const editForm = document.getElementById('editProfileForm');
    if (editForm) {
        editForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const token = localStorage.getItem(TOKEN_STORAGE_KEY);
            const payload = {
                first_name: document.getElementById('editFirstName').value.trim(),
                last_name: document.getElementById('editLastName').value.trim(),
                email: document.getElementById('editEmail').value.trim() || null,
                shipping_address: document.getElementById('editShipping').value.trim() || null
            };
            try {
                const res = await fetch(`${API_BASE_URL}/clients/me`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json', 'X-Auth-Token': token },
                    body: JSON.stringify(payload)
                });
                const updatedClient = await res.json();
                if (!res.ok) throw new Error(updatedClient.detail || '╨Я╨╛╨╝╨╕╨╗╨║╨░ ╨╛╨╜╨╛╨▓╨╗╨╡╨╜╨╜╤П ╨┐╤А╨╛╤Д╤Ц╨╗╤О');

                currentClient = updatedClient;
                showMainScreen(currentClient);
                showToast('╨Я╤А╨╛╤Д╤Ц╨╗╤М ╤Г╤Б╨┐╤Ц╤И╨╜╨╛ ╨╛╨╜╨╛╨▓╨╗╨╡╨╜╨╛!');
                closeEditProfileModal();
            } catch (err) {
                showToast(err.message, 'error');
            }
        });
    }
}
