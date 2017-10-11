#include <stdio.h>
#include "hocdec.h"
extern int nrnmpi_myid;
extern int nrn_nobanner_;

extern void _CaT_reg(void);
extern void _Cad_reg(void);
extern void _IL_reg(void);
extern void _NMDA_reg(void);
extern void _PlateauConductance_reg(void);
extern void _ampa_reg(void);
extern void _ca_reg(void);
extern void _gabaa_reg(void);
extern void _gabab_reg(void);
extern void _glutamate_reg(void);
extern void _kadist_reg(void);
extern void _kaprox_reg(void);
extern void _kv_reg(void);
extern void _na_reg(void);
extern void _vecstim_reg(void);
extern void _vmax_reg(void);

void modl_reg(){
  if (!nrn_nobanner_) if (nrnmpi_myid < 1) {
    fprintf(stderr, "Additional mechanisms from files\n");

    fprintf(stderr," CaT.mod");
    fprintf(stderr," Cad.mod");
    fprintf(stderr," IL.mod");
    fprintf(stderr," NMDA.mod");
    fprintf(stderr," PlateauConductance.mod");
    fprintf(stderr," ampa.mod");
    fprintf(stderr," ca.mod");
    fprintf(stderr," gabaa.mod");
    fprintf(stderr," gabab.mod");
    fprintf(stderr," glutamate.mod");
    fprintf(stderr," kadist.mod");
    fprintf(stderr," kaprox.mod");
    fprintf(stderr," kv.mod");
    fprintf(stderr," na.mod");
    fprintf(stderr," vecstim.mod");
    fprintf(stderr," vmax.mod");
    fprintf(stderr, "\n");
  }
  _CaT_reg();
  _Cad_reg();
  _IL_reg();
  _NMDA_reg();
  _PlateauConductance_reg();
  _ampa_reg();
  _ca_reg();
  _gabaa_reg();
  _gabab_reg();
  _glutamate_reg();
  _kadist_reg();
  _kaprox_reg();
  _kv_reg();
  _na_reg();
  _vecstim_reg();
  _vmax_reg();
}
