# scripts/initialize_profile_pictures.py
from sqlmodel import Session
from models.database.profile_picture import VPProfilePicture
from core.database import engine

def initialize_profile_pictures():
    profile_pictures = [
        {
            "name": "Ethan",
            "image_url": "https://bruvvsssoqnlwamndcmx.supabase.co/storage/v1/object/sign/vp-profile-pictures/wolfskranz2810_handsome_professional_male_Chinese-Singapoean__ecb1dde0-7291-49fa-ab99-67534ffeb21e_0.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJ2cC1wcm9maWxlLXBpY3R1cmVzL3dvbGZza3JhbnoyODEwX2hhbmRzb21lX3Byb2Zlc3Npb25hbF9tYWxlX0NoaW5lc2UtU2luZ2Fwb2Vhbl9fZWNiMWRkZTAtNzI5MS00OWZhLWFiOTktNjc1MzRmZmViMjFlXzAucG5nIiwiaWF0IjoxNzM1NTQ4ODQ1LCJleHAiOjE3MzYxNTM2NDV9.n0bI7Dke8dpmsdcIBq71j5DFCPo25uZAMg7OzPqF4w0&t=2024-12-30T08%3A54%3A05.047Z",
            "display_order": 1,
            "is_active": True
        },
        {
            "name": "Liam",
            "image_url": "https://bruvvsssoqnlwamndcmx.supabase.co/storage/v1/object/sign/vp-profile-pictures/wolfskranz2810_handsome_professional_male_Chinese-Singaporean_30023cc7-62d5-4807-8382-cf55aa5a28a9_0.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJ2cC1wcm9maWxlLXBpY3R1cmVzL3dvbGZza3JhbnoyODEwX2hhbmRzb21lX3Byb2Zlc3Npb25hbF9tYWxlX0NoaW5lc2UtU2luZ2Fwb3JlYW5fMzAwMjNjYzctNjJkNS00ODA3LTgzODItY2Y1NWFhNWEyOGE5XzAucG5nIiwiaWF0IjoxNzM1NTQ4ODY5LCJleHAiOjE3MzYxNTM2Njl9.wirSQCRti7FPdoeNmNKRqxmFsvqHtCeX8e9Yemf1Tsk&t=2024-12-30T08%3A54%3A29.569Z",
            "display_order": 2,
            "is_active": True
        },
        {
            "name": "Noah",
            "image_url": "https://bruvvsssoqnlwamndcmx.supabase.co/storage/v1/object/sign/vp-profile-pictures/wolfskranz2810_handsome_professional_male_Irish_mid-30s_forma_45a15fe2-79ea-493c-9c97-6d6c7d46c7ce_1.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJ2cC1wcm9maWxlLXBpY3R1cmVzL3dvbGZza3JhbnoyODEwX2hhbmRzb21lX3Byb2Zlc3Npb25hbF9tYWxlX0lyaXNoX21pZC0zMHNfZm9ybWFfNDVhMTVmZTItNzllYS00OTNjLTljOTctNmQ2YzdkNDZjN2NlXzEucG5nIiwiaWF0IjoxNzM1NTQ4ODc4LCJleHAiOjE3MzYxNTM2Nzh9.FJI72KKaBqiXM1mpq3jPEBnprmNPERTKhoNCg_ywEVA&t=2024-12-30T08%3A54%3A38.281Z",
            "display_order": 3,
            "is_active": True
        },
        {
            "name": "Caleb",
            "image_url": "https://bruvvsssoqnlwamndcmx.supabase.co/storage/v1/object/sign/vp-profile-pictures/wolfskranz2810_handsome_professional_male_Irish_mid-30s_forma_91b1b6f1-c50f-43d9-861f-eefde77556e5_1.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJ2cC1wcm9maWxlLXBpY3R1cmVzL3dvbGZza3JhbnoyODEwX2hhbmRzb21lX3Byb2Zlc3Npb25hbF9tYWxlX0lyaXNoX21pZC0zMHNfZm9ybWFfOTFiMWI2ZjEtYzUwZi00M2Q5LTg2MWYtZWVmZGU3NzU1NmU1XzEucG5nIiwiaWF0IjoxNzM1NTQ4ODg4LCJleHAiOjE3MzYxNTM2ODh9.zH83kVh2na0Fm_NJMP5zs8gagGjcRaJ_jUOyUD1-dCI&t=2024-12-30T08%3A54%3A48.905Z",
            "display_order": 4,
            "is_active": True
        },
        {
            "name": "Ava",
            "image_url": "https://bruvvsssoqnlwamndcmx.supabase.co/storage/v1/object/sign/vp-profile-pictures/wolfskranz2810_Generate_a_highly_photorealistic_high-resoluti_a13c2c58-019e-4a3d-8ab2-d798f46cfef8_0.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJ2cC1wcm9maWxlLXBpY3R1cmVzL3dvbGZza3JhbnoyODEwX0dlbmVyYXRlX2FfaGlnaGx5X3Bob3RvcmVhbGlzdGljX2hpZ2gtcmVzb2x1dGlfYTEzYzJjNTgtMDE5ZS00YTNkLThhYjItZDc5OGY0NmNmZWY4XzAucG5nIiwiaWF0IjoxNzM1NTQ4NzAxLCJleHAiOjE3MzYxNTM1MDF9.Fms3C34CbV1xFDHNZfKrZ9aMF-ppPkc2pqns7gyuwbk&t=2024-12-30T08%3A51%3A41.939Z",
            "display_order": 5,
            "is_active": True
        },
        {
            "name": "Grace",
            "image_url": "https://bruvvsssoqnlwamndcmx.supabase.co/storage/v1/object/sign/vp-profile-pictures/wolfskranz2810_Generate_a_highly_photorealistic_high-resoluti_a63e4c65-a4b5-424a-bc6a-bfd51f62ba95_3.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJ2cC1wcm9maWxlLXBpY3R1cmVzL3dvbGZza3JhbnoyODEwX0dlbmVyYXRlX2FfaGlnaGx5X3Bob3RvcmVhbGlzdGljX2hpZ2gtcmVzb2x1dGlfYTYzZTRjNjUtYTRiNS00MjRhLWJjNmEtYmZkNTFmNjJiYTk1XzMucG5nIiwiaWF0IjoxNzM1NTQ4Nzk3LCJleHAiOjE3MzYxNTM1OTd9.0cVJzH5fFnBHVMbmCn6mL5SFzCdMWghACJFBouYzppY&t=2024-12-30T08%3A53%3A17.254Z",
            "display_order": 6,
            "is_active": True
        },
        {
            "name": "Mia",
            "image_url": "https://bruvvsssoqnlwamndcmx.supabase.co/storage/v1/object/sign/vp-profile-pictures/wolfskranz2810_good-looking_professional_female_Asian-America_680e613f-d35f-4cae-b96f-f3f2ecf31f3f_3.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJ2cC1wcm9maWxlLXBpY3R1cmVzL3dvbGZza3JhbnoyODEwX2dvb2QtbG9va2luZ19wcm9mZXNzaW9uYWxfZmVtYWxlX0FzaWFuLUFtZXJpY2FfNjgwZTYxM2YtZDM1Zi00Y2FlLWI5NmYtZjNmMmVjZjMxZjNmXzMucG5nIiwiaWF0IjoxNzM1NTQ4ODE4LCJleHAiOjE3MzYxNTM2MTh9.wIVAtkChroGFWu30vH5B5kkQjXRlFjwgEza_cpceBIo&t=2024-12-30T08%3A53%3A38.411Z",
            "display_order": 7,
            "is_active": True
        },
        {
            "name": "Zoe",
            "image_url": "https://bruvvsssoqnlwamndcmx.supabase.co/storage/v1/object/sign/vp-profile-pictures/wolfskranz2810_gorgeous_professional_female_Chinese-Singapore_257f1647-4239-497c-ac27-fffff53be054_2.png?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJ2cC1wcm9maWxlLXBpY3R1cmVzL3dvbGZza3JhbnoyODEwX2dvcmdlb3VzX3Byb2Zlc3Npb25hbF9mZW1hbGVfQ2hpbmVzZS1TaW5nYXBvcmVfMjU3ZjE2NDctNDIzOS00OTdjLWFjMjctZmZmZmY1M2JlMDU0XzIucG5nIiwiaWF0IjoxNzM1NTQ4ODMyLCJleHAiOjE3MzYxNTM2MzJ9.e1c_Fp4bvrWWiEa_mDiEr9xxCYrV9474rRIgSrVUNCY&t=2024-12-30T08%3A53%3A52.088Z",
            "display_order": 8,
            "is_active": True
        },
    ]
    
    with Session(engine) as session:
        # Check if pictures already exist
        existing = session.query(VPProfilePicture).count()
        if existing == 0:
            for picture in profile_pictures:
                db_picture = VPProfilePicture(**picture)
                session.add(db_picture)
            session.commit()

if __name__ == "__main__":
    initialize_profile_pictures()