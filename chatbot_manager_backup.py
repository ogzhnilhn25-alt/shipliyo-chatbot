    def get_recent_sms_by_site(self, site: str, seconds: int = 120, language: str = 'tr') -> Dict:
        try:
            print(f"🔍 ARAMA: Site='{site}', Saniye={seconds}")

            if not self.db_connected:
                print("❌ PostgreSQL bağlı değil")
                return {
                    "success": False,
                    "response": self.response_manager.get_response('no_recent_sms', language).format(
                        site=site.title(),
                        seconds=seconds
                    ),
                    "response_type": "direct",
                    "source": "postgresql_disconnected"
                }

            # ✅ UTC zamanını kullan
            time_threshold = datetime.now(timezone.utc) - timedelta(seconds=seconds)
            
            print(f"⏰ UTC Zaman filtresi: {time_threshold}")

            conn = self.get_db_connection()
            if not conn:
                return {
                    "success": False,
                    "response": self.response_manager.get_response('no_recent_sms', language).format(
                        site=site.title(),
                        seconds=seconds
                    ),
                    "response_type": "direct",
                    "source": "postgresql"
                }

            cur = conn.cursor()
            
            if site == 'other':
                # ✅ DİĞER SİTELER: Trendyol, Hepsiburada, n11 hariç tüm SMS'ler
                cur.execute(
                    "SELECT * FROM sms_messages WHERE body NOT ILIKE %s AND body NOT ILIKE %s AND body NOT ILIKE %s AND timestamp >= %s ORDER BY timestamp DESC LIMIT 10",
                    ('%trendyol%', '%hepsiburada%', '%n11%', time_threshold)
                )
            else:
                # ✅ BELİRLİ SİTE: Sadece body içeriğine göre filtrele
                site_patterns = {
                    'trendyol': '%trendyol%',
                    'hepsiburada': '%hepsiburada%', 
                    'n11': '%n11%'
                }
                search_pattern = site_patterns.get(site, f'%{site}%')
                
                cur.execute(
                    "SELECT * FROM sms_messages WHERE body ILIKE %s AND timestamp >= %s ORDER BY timestamp DESC LIMIT 10",
                    (search_pattern, time_threshold)
                )

            recent_sms = cur.fetchall()
            cur.close()
            conn.close()

            print(f"📨 Bulunan SMS sayısı: {len(recent_sms)}")
            
            # ✅ DEBUG: Bulunan SMS'leri göster
            for sms in recent_sms:
                print(f"📄 SMS: {sms}")

            if not recent_sms:
                return {
                    "success": False,
                    "response": self.response_manager.get_response('no_recent_sms', language).format(
                        site=site.title(),
                        seconds=seconds
                    ),
                    "response_type": "direct",
                    "source": "postgresql"
                }

            # PostgreSQL sonuçlarını dictionary'ye çevir
            parsed_sms_list = []
            for sms in recent_sms:
                sms_dict = {
                    'body': sms[2],  # body sütunu
                    'timestamp': sms[3]  # timestamp sütunu
                }
                parsed_sms = self.sms_parser.parse_sms(sms_dict['body'], language)
                parsed_sms_list.append(parsed_sms)

            print(f"🔧 Parsed SMS List: {parsed_sms_list}")

            if len(parsed_sms_list) == 1:
                sms = parsed_sms_list[0]
                return {
                    "success": True,
                    "response": self.response_manager.get_response('reference_found', language).format(
                        site=sms['site'].title(),
                        code=sms['verification_code']
                    ),
                    "response_type": "direct",
                    "data": sms,
                    "source": "postgresql"
                }
            else:
                sms_details = [
                    {"site": sms['site'].title(), "code": sms['verification_code'], "raw": sms.get('raw', '')}
                    for sms in parsed_sms_list
                ]
                response_text = self.response_manager.get_response('multiple_sms_found', language).format(
                    count=len(parsed_sms_list),
                    seconds=seconds
                )
                return {
                    "success": True,
                    "response": response_text,
                    "response_type": "list",
                    "sms_list": sms_details,
                    "source": "postgresql"
                }

        except Exception as e:
            print(f"❌ PostgreSQL sorgu hatası: {e}")
            return {
                "success": False,
                "response": self.response_manager.get_response('no_recent_sms', language).format(
                    site=site.title(),
                    seconds=seconds
                ),
                "response_type": "direct",
                "source": "error"
            }